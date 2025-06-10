import copy
import glob
import numpy as np
import os
import shutil
import zipfile

import romsearch
from .romcompressor import ROMCompressor
from .rompatcher import ROMPatcher
from ..util import (
    get_directory_name,
    centred_string,
    load_yml,
    setup_logger,
    unzip_file,
    load_json,
    save_json,
)

COMPRESSION_FILES = {
    "chdman": [".bin", ".cue"],
}


def create_m3u(
    m3u_file,
    out_files,
    relative_dir=None,
):
    """Create an m3u playlist file for multi-disc games

    Args:
        m3u_file (str): Path to the m3u file.
        out_files (list): List of files to put into m3u file.
        relative_dir: If not None, will append this relative directory
            to each out file. Defaults to None.
    """

    with open(m3u_file, "w+") as f:

        for o in out_files:
            if relative_dir is not None:
                o = f"{relative_dir}/{o}"
            f.write(f"{o}\n")

    return True


class ROMMover:

    def __init__(
        self,
        platform,
        config_file=None,
        config=None,
        platform_config=None,
        regex_config=None,
        logger=None,
        log_line_sep="=",
        log_line_length=100,
    ):
        """ROM Moving and cache updating tool

        Because we do this per-platform, per-game, they need to be specified here

        Args:
            platform (str): Platform name
            config_file (str, optional): path to config file. Defaults to None.
            config (dict, optional): configuration dictionary. Defaults to None.
            platform_config (dict, optional): platform configuration dictionary. Defaults to None.
            regex_config (dict, optional): regex configuration dictionary. Defaults to None.
            logger (logging.Logger, optional): logger. Defaults to None.
            log_line_length (int, optional): Line length of log. Defaults to 100
        """

        if config_file is None and config is None:
            raise ValueError("config_file or config must be specified")

        if config is None:
            config = load_yml(config_file)
        self.config = config

        if logger is None:
            log_dir = self.config.get("dirs", {}).get(
                "log_dir", os.path.join(os.getcwd(), "logs")
            )
            logger_add_dir = str(os.path.join(platform))
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(
                log_level=log_level,
                script_name=f"ROMMover",
                log_dir=log_dir,
                additional_dir=logger_add_dir,
            )
        self.logger = logger

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

        # Pull in directories
        self.raw_dir = self.config.get("dirs", {}).get("raw_dir", None)
        if self.raw_dir is None:
            raise ValueError("raw_dir needs to be defined in config")

        self.rom_dir = self.config.get("dirs", {}).get("rom_dir", None)
        if self.rom_dir is None:
            raise ValueError("rom_dir needs to be defined in config")

        # Whether we'll separate directories or not
        self.separate_directories = self.config.get("romsearch", {}).get(
            "separate_directories", True
        )

        # Whether we'll handle multi-disc files or not
        self.handle_multi_discs = self.config.get("romsearch", {}).get(
            "handle_multi_discs", False
        )

        self.run_rompatcher = self.config.get("romsearch", {}).get(
            "run_rompatcher", False
        )
        self.patch_dir = self.config.get("dirs", {}).get("patch_dir", None)
        if self.patch_dir is None and self.run_rompatcher:
            raise ValueError("patch_dir needs to be defined in config")

        cache_dir = self.config.get("dirs", {}).get("cache_dir", os.getcwd())
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        cache_file = os.path.join(cache_dir, f"cache ({platform}).json")

        if os.path.exists(cache_file):
            cache = load_json(cache_file)
        else:
            cache = {}

        self.platform = platform
        self.cache_file = cache_file
        self.cache = cache

        # Pull in platform config that we need
        mod_dir = os.path.dirname(romsearch.__file__)

        if platform_config is None:
            platform_config_file = os.path.join(
                mod_dir, "configs", "platforms", f"{platform}.yml"
            )
            platform_config = load_yml(platform_config_file)
        self.platform_config = platform_config

        if regex_config is None:
            regex_file = os.path.join(mod_dir, "configs", "regex.yml")
            regex_config = load_yml(regex_file)
        self.regex_config = regex_config

        self.unzip = self.platform_config.get("unzip", False)
        self.compress = self.platform_config.get("compress", False)
        self.compress_method = self.platform_config.get("compress_method", None)

        # If we have compression on, we need to define a compression method
        if self.compress and self.compress_method is None:
            raise ValueError("compress_method needs to be defined if compressing")

        # If we have compression, make sure we have a path to the tool defined
        self.compress_method_path = self.config.get("romcompressor", {}).get(
            f"{self.compress_method}_path", None
        )
        if self.compress and self.compress_method_path is None:
            self.logger.error(
                centred_string(
                    f"{self.compress_method}_path needs to be defined in the user config if compressing."
                    f"Disabling compression",
                    total_length=self.log_line_length,
                )
            )
            self.compress = False

    def run(
        self,
        rom_dict,
    ):
        """Run the ROMMover

        Args:
            rom_dict (dict): ROM dictionary
        """

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")
        self.logger.info(
            centred_string(
                f"Running ROMMover for {self.platform}",
                total_length=self.log_line_length,
            )
        )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        roms_moved = self.move_roms(rom_dict)
        self.save_cache()

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        return roms_moved

    def move_roms(self, all_rom_dict):
        """Actually move the roms

        Args:
            all_rom_dict (dict): ROM dictionary for everything
        """

        roms_moved = []

        all_multi_discs = {}

        total_games = len(all_rom_dict)

        for game_no, game in enumerate(all_rom_dict):
            rom_dict = all_rom_dict[game]

            for rom_no, rom in enumerate(rom_dict):

                # Because the filename can change, keep it here
                full_name = copy.deepcopy(rom_dict[rom]["full_name"])
                rom_file = copy.deepcopy(rom_dict[rom]["download_name"])
                short_name = copy.deepcopy(rom_dict[rom]["short_name"])

                # If we're either a superset or a compilation, then
                # inherit a game and directory name from the ROM
                # instead. This will avoid multiple downloads in
                # some circumstances
                is_superset = rom_dict[rom].get("is_superset", False)
                is_compilation = rom_dict[rom].get("is_compilation", False)

                # Pull out a clean directory name and disc-free name in case we need it
                if is_superset or is_compilation:
                    dir_name = get_directory_name(full_name)
                    game = copy.deepcopy(short_name)
                else:
                    dir_name = str(copy.deepcopy(rom_dict[rom]["dir_name"]))

                # Keep track of what this original directory name is, since we might need
                # it
                dir_name_original = copy.deepcopy(dir_name)

                disc_free_name = str(copy.deepcopy(rom_dict[rom]["disc_free_name"]))

                cache_mod_time = (
                    self.cache.get(self.platform, {})
                    .get(game, {})
                    .get(rom, {})
                    .get("file_mod_time", 0)
                )

                # Figure out if we're patching the ROM, based on whether it's already been patched
                # and if there's a patch file
                rom_patched = (
                    self.cache.get(self.platform, {})
                    .get(game, {})
                    .get(rom, {})
                    .get("patched", False)
                )
                patch_url = rom_dict.get(rom, {}).get("patch_file", "")

                to_patch_rom = False
                if not rom_patched and patch_url != "" and self.run_rompatcher:
                    to_patch_rom = True

                # Keep track if we're expecting a patched file
                expecting_patched_rom = False
                if patch_url != "" and self.run_rompatcher:
                    expecting_patched_rom = True

                # Keep track of absolute directories and relative directories to the
                # platform itself, for cache reasons
                if self.separate_directories:
                    out_dir = os.path.join(self.rom_dir, self.platform, dir_name)
                    out_base_dir = copy.deepcopy(dir_name)
                else:
                    out_dir = os.path.join(self.rom_dir, self.platform)
                    out_base_dir = ""

                # Skip if the file modification time matches the one in the cache, we're not patching, and the
                # destination file exists

                # If we're handling multi-disc files, and we have a multi-disc file, then make the output
                # directory a hidden one
                if rom_dict[rom]["multi_disc"] and self.handle_multi_discs:

                    m3u_out_dir = copy.deepcopy(out_dir)
                    out_dir = os.path.join(str(out_dir), f".{disc_free_name}")

                    # Also update the dir name, since we use that later
                    game_dir_name = copy.deepcopy(out_base_dir)
                    out_base_dir = os.path.join(out_base_dir, f".{disc_free_name}")

                    if disc_free_name not in all_multi_discs:
                        all_multi_discs[disc_free_name] = {
                            "m3u_out_dir": m3u_out_dir,
                            "game": dir_name_original,
                            "game_dir_name": game_dir_name,
                            "relative_dir": f".{disc_free_name}",
                            "out_files": [],
                        }

                # Loop over here, since the extensions might change. Search specifically by the filename
                # to make things quicker
                rom_file_no_ext = os.path.splitext(rom_file)[0]
                out_files = glob.glob(os.path.join(str(out_dir), f"{rom_file_no_ext}*"))
                short_out_files = [os.path.basename(o) for o in out_files]

                final_file_exists = False
                final_file_name = None

                # First, search for an exact match, but only if we're not unzipping
                if not self.unzip and not to_patch_rom:
                    for o in short_out_files:

                        if final_file_exists:
                            continue

                        if o == rom_file:
                            final_file_exists = True
                            final_file_name = os.path.basename(o)

                # If we have unzip and compress set on, then we need to
                # figure out which we're actually doing
                unzip = copy.deepcopy(self.unzip)
                compress = copy.deepcopy(self.compress)

                if self.unzip and self.compress:

                    raw_file = os.path.join(self.raw_dir, self.platform, rom_file)

                    compress_suitable = self.check_compress_suitable(raw_file)
                    if compress_suitable:
                        unzip = False
                        compress = True
                    else:
                        unzip = True
                        compress = False

                # If we're unzipping (and potentially patching), then pull the expected files out here and check again
                if unzip or expecting_patched_rom:

                    final_file_exists, final_file_name = self.check_files_exist(
                        rom=rom_file,
                        files=short_out_files,
                        file_ext_key="file_exts",
                        patched_rom=expecting_patched_rom,
                    )

                # If we're compressing, then pull the expected files out here and check again
                if compress:

                    final_file_exists, final_file_name = self.check_files_exist(
                        rom=rom_file,
                        files=short_out_files,
                        file_ext_key="compress_file_exts",
                        patched_rom=expecting_patched_rom,
                    )

                # If nothing has changed, then move on
                if (
                    rom_dict[rom]["file_mod_time"] == cache_mod_time
                    and final_file_exists
                ):
                    self.logger.info(
                        centred_string(
                            f"[{game_no + 1}/{total_games}]: No updates for {rom}, skipping",
                            total_length=self.log_line_length,
                        )
                    )

                    # Make sure we keep track of multi-disc stuff, even if we're not necessarily changing it
                    if rom_dict[rom]["multi_disc"] and self.handle_multi_discs:
                        if isinstance(final_file_name, str):
                            final_file_name = [final_file_name]
                            all_multi_discs[disc_free_name]["out_files"].extend(
                                final_file_name
                            )

                    # Gracefully update the cache from earlier versions
                    cache_files = (
                        self.cache.get(self.platform, {})
                        .get(game, {})
                        .get(rom, {})
                        .get("all_files", [])
                    )

                    if len(cache_files) == 0:

                        # Log whether we've patched or not
                        patched = False
                        if expecting_patched_rom:
                            patched = True
                        rom_dict[rom]["patched"] = patched

                        # Update the cache
                        self.cache_update(
                            game=game,
                            rom=rom,
                            files=short_out_files,
                            out_dir=out_base_dir,
                            rom_dict=rom_dict,
                        )

                    continue

                # We need to keep track of output files
                out_files = []

                # If we're patching ROMs, then do that here
                if to_patch_rom:

                    rom_patch_file = os.path.join(self.raw_dir, self.platform, rom_file)

                    patcher = ROMPatcher(
                        platform=self.platform,
                        config=self.config,
                        platform_config=self.platform_config,
                        regex_config=self.regex_config,
                        logger=self.logger,
                        log_line_length=self.log_line_length,
                    )

                    full_rom = patcher.run(
                        file=str(rom_patch_file),
                        patch_url=patch_url,
                        rom_dict=rom_dict[rom],
                    )

                    unzip = False
                    patched = True

                else:
                    full_dir = os.path.join(self.raw_dir, self.platform)
                    full_rom = os.path.join(str(full_dir), rom_file)

                    patched = False

                # If we're compressing ROMs, do that here
                if compress:

                    if to_patch_rom:
                        raise NotImplementedError(
                            "Currently cannot handle compressing of patched files"
                        )

                    rom_compress_file = os.path.join(
                        self.raw_dir, self.platform, rom_file
                    )

                    full_rom = self.compress_file(
                        rom_compress_file,
                    )

                # Log whether we've patched or not
                rom_dict[rom]["patched"] = patched

                # Move the main file. Don't delete folders as the game and the out directory
                # don't necessarily match
                move_file_success, moved_files = self.move_file(
                    full_rom, game=game, out_dir=out_dir, unzip=unzip
                )

                if not move_file_success:
                    self.logger.warning(
                        centred_string(
                            f"[{game_no + 1}/{total_games}]: {rom_file} not found in raw directory, skipping",
                            total_length=self.log_line_length,
                        )
                    )
                    continue

                out_files.extend(moved_files)

                self.logger.info(
                    centred_string(
                        f"[{game_no + 1}/{total_games}]: Moved {rom_file}",
                        total_length=self.log_line_length,
                    )
                )

                # If there are additional files to move/unzip, do that now
                if "subchannels" in self.platform_config:
                    for subchannel in self.platform_config["subchannels"]:

                        add_full_dir = os.path.join(
                            self.raw_dir, f"{self.platform} {subchannel}"
                        )
                        add_file = os.path.join(add_full_dir, rom_file)
                        if os.path.exists(add_file):

                            # These files should *always* be unzipped
                            move_file_success, moved_files = self.move_file(
                                add_file, game=game, out_dir=out_dir, unzip=True
                            )

                            if not move_file_success:
                                self.logger.warning(
                                    centred_string(
                                        f"{rom_file} {subchannel} not found in raw directory, skipping",
                                        total_length=self.log_line_length,
                                    )
                                )
                            else:
                                self.logger.info(
                                    centred_string(
                                        f"[{game_no + 1}/{total_games}]: Moved {rom_file} ({subchannel})",
                                        total_length=self.log_line_length,
                                    )
                                )
                                out_files.extend(moved_files)

                # Add these to the multi-disc dictionary, if needed
                if rom_dict[rom]["multi_disc"] and self.handle_multi_discs:
                    all_multi_discs[disc_free_name]["out_files"].extend(out_files)

                # Update and save the cache
                self.cache_update(
                    game=game,
                    rom=rom,
                    files=out_files,
                    out_dir=out_base_dir,
                    rom_dict=rom_dict,
                )
                self.save_cache()

                roms_moved.append(rom_file)

        # Handle the multi-disc files by generating m3u playlists
        if self.handle_multi_discs and len(all_multi_discs) > 0:

            for multi_disc in all_multi_discs:

                # Get the full m3u file name
                m3u_file_name = f"{multi_disc}.m3u"
                m3u_full_file_name = os.path.join(
                    all_multi_discs[multi_disc]["m3u_out_dir"], m3u_file_name
                )

                # Assume that by sorting we're good on the file order
                out_files = sorted(all_multi_discs[multi_disc]["out_files"])

                # If we already have this file, then continue on
                if os.path.exists(m3u_full_file_name):
                    continue

                # Or, create the m3u and put this into the cache
                else:
                    create_m3u(
                        m3u_file=m3u_full_file_name,
                        out_files=out_files,
                        relative_dir=all_multi_discs[multi_disc]["relative_dir"],
                    )
                    self.cache_update_multi_disc(
                        game=all_multi_discs[multi_disc]["game"],
                        m3u_name=f"{multi_disc} [Multi Disc]",
                        files=[m3u_file_name],
                        out_dir=all_multi_discs[multi_disc]["game_dir_name"],
                    )
                    self.save_cache()

                    self.logger.info(
                        centred_string(
                            f"Created {m3u_file_name}",
                            total_length=self.log_line_length,
                        )
                    )

        return roms_moved

    def check_files_exist(
        self,
        rom,
        files,
        file_ext_key,
        patched_rom=False,
    ):
        """Check files exist, so we know whether to move things around or not

        Args:
            rom: ROM name
            files: List of existing files
            file_ext_key: Potential file extensions
            patched_rom: Whether ROM is patched or not. Defaults to False
        """

        final_file_exists = False
        final_file_name = None

        # Pull potential file extensions out
        file_exts = self.platform_config.get(file_ext_key, [])
        if len(file_exts) == 0:
            raise ValueError(
                "ROM file extensions should be defined in the platform config"
            )

        rom_no_ext = os.path.splitext(rom)[0]

        # Add in that this has been patched, if necessary
        if patched_rom:
            rom_no_ext += " (ROMPatched)"

        # Loop over the files, loop over the ROM file extensions, look for a match
        for o in files:
            for file_ext in file_exts:
                rom_w_ext = rom_no_ext + file_ext

                if o == rom_w_ext:
                    final_file_exists = True
                    final_file_name = os.path.basename(o)

        return final_file_exists, final_file_name

    def check_compress_suitable(
        self,
        rom_file,
    ):
        """Check if a file is suitable for compression given compression method

        Args:
            rom_file: File to check
        """

        with zipfile.ZipFile(rom_file, "r") as zip_file:
            # Get the names of all the files in the zip file
            names = zip_file.namelist()

            name_exts = np.unique([os.path.splitext(n)[-1] for n in names])
            name_exts = [str(n) for n in name_exts]
            name_exts.sort()

        if name_exts == COMPRESSION_FILES[self.compress_method]:
            compress_suitable = True
        else:
            compress_suitable = False

        return compress_suitable

    def move_file(
        self,
        zip_file_name,
        game,
        out_dir=None,
        unzip=False,
        delete_folder=False,
    ):
        """Move file to directory structure, optionally unzipping"""

        moved_files = []

        # If the file doesn't exist, crash out
        if not os.path.exists(zip_file_name):
            return False, moved_files

        # If we don't have an output directory, set one from the game name
        if out_dir is None:
            out_dir = os.path.join(self.rom_dir, self.platform, game)

        if delete_folder and os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_dir = str(out_dir)

        if unzip:
            unzipped_files = unzip_file(zip_file_name, out_dir)
            moved_files.extend(unzipped_files)
        else:
            short_zip_file = os.path.split(zip_file_name)[-1]
            out_file = os.path.join(out_dir, short_zip_file)

            # Remove this file if it already exists
            if os.path.exists(out_file):
                os.remove(out_file)

            os.link(zip_file_name, out_file)
            moved_files.append(short_zip_file)

        return True, moved_files

    def compress_file(
        self,
        rom,
    ):
        """Compress a file

        Args:
            rom: ROM name
        """

        rc = ROMCompressor(
            platform=self.platform,
            config=self.config,
            compress_method=self.compress_method,
            compress_method_path=self.compress_method_path,
            logger=self.logger,
            log_line_length=self.log_line_length,
            log_line_sep=self.log_line_sep,
        )

        compressed_file = rc.run(rom)

        return compressed_file

    def cache_update(
        self,
        game,
        rom,
        files,
        out_dir,
        rom_dict,
    ):
        """Update the cache with new file data

        Args:
            game: Game name
            rom: ROM name for dictionary info
            files: List of files to save to cache
            out_dir: Output directory for files, relative to [rom_dir]/[platform]
            rom_dict: Dictionary of ROM properties
        """

        # If we don't have dictionaries already set, create
        if self.platform not in self.cache:
            self.cache[self.platform] = {}

        if game not in self.cache[self.platform]:
            self.cache[self.platform][game] = {}

        if not self.cache[self.platform][game]:
            self.cache[self.platform][game] = {}

        # Include info about whether the ROM has been patched or not,
        # the patch file, and all the files we've included and where
        # we've put em

        self.cache[self.platform][game][rom] = {
            "file_mod_time": rom_dict[rom]["file_mod_time"],
            "patch_file": rom_dict[rom]["patch_file"],
            "patched": rom_dict[rom]["patched"],
            "output_directory": out_dir,
            "all_files": files,
        }

    def cache_update_multi_disc(
        self,
        game,
        m3u_name,
        files,
        out_dir,
    ):
        """Update the cache with m3u playlist info

        Args:
            game: Game name
            m3u_name: m3u playlist name to save to cache
            files: List of files to save to cache
            out_dir: Output directory for files, relative to [rom_dir]/[platform]
        """

        # If we don't have dictionaries already set, create
        if self.platform not in self.cache:
            self.cache[self.platform] = {}

        if game not in self.cache[self.platform]:
            self.cache[self.platform][game] = {}

        if not self.cache[self.platform][game]:
            self.cache[self.platform][game] = {}

        # Include just info on where the m3u file is, and that it's a multi-disc file
        self.cache[self.platform][game][m3u_name] = {
            "multi_disc": True,
            "output_directory": out_dir,
            "all_files": files,
        }

    def save_cache(self):
        """Save out the cache file"""

        cache = copy.deepcopy(self.cache)
        save_json(cache, self.cache_file, sort_key=self.platform)
