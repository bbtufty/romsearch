import copy
import glob
import os
import shutil

import romsearch
from .rompatcher import ROMPatcher
from ..util import (
    centred_string,
    load_yml,
    setup_logger,
    unzip_file,
    load_json,
    save_json,
)


class ROMMover:

    def __init__(
        self,
        platform,
        game,
        config_file=None,
        config=None,
        platform_config=None,
        logger=None,
        log_line_sep="=",
        log_line_length=100,
    ):
        """ROM Moving and cache updating tool

        Because we do this per-platform, per-game, they need to be specified here

        Args:
            platform (str): Platform name
            game (str): Game name
            config_file (str, optional): path to config file. Defaults to None.
            config (dict, optional): configuration dictionary. Defaults to None.
            platform_config (dict, optional): platform configuration dictionary. Defaults to None.
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
            logger_add_dir = str(os.path.join(platform, game))
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(
                log_level=log_level,
                script_name=f"ROMMover",
                log_dir=log_dir,
                additional_dir=logger_add_dir,
            )
        self.logger = logger

        # Pull in directories
        self.raw_dir = self.config.get("dirs", {}).get("raw_dir", None)
        if self.raw_dir is None:
            raise ValueError("raw_dir needs to be defined in config")

        self.rom_dir = self.config.get("dirs", {}).get("rom_dir", None)
        if self.rom_dir is None:
            raise ValueError("rom_dir needs to be defined in config")

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
        self.game = game
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

        self.unzip = self.platform_config.get("unzip", False)

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(
        self,
        rom_dict,
    ):

        roms_moved = self.move_roms(rom_dict)
        self.save_cache()

        return roms_moved

    def move_roms(self, rom_dict):
        """Actually move the roms"""

        roms_moved = []

        for rom_no, rom in enumerate(rom_dict):

            # Pull out a clean directory name
            dir_name = str(copy.deepcopy(rom_dict[rom]["dir_name"]))

            cache_mod_time = (
                self.cache.get(self.platform, {})
                .get(self.game, {})
                .get(rom, {})
                .get("file_mod_time", 0)
            )

            # Figure out if we're patching the ROM, based on whether it's already been patched
            # and if there's a patch file
            rom_patched = (
                self.cache.get(self.platform, {})
                .get(self.game, {})
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

            # Skip if the file modification time matches the one in the cache, we're not patching, and the
            # destination file exists
            out_dir = os.path.join(self.rom_dir, self.platform, dir_name)

            # Loop over here, since the extensions might change
            out_files = glob.glob(os.path.join(out_dir, "*"))
            short_out_files = [os.path.basename(o) for o in out_files]

            final_file_exists = False

            # First, search for an exact match, but only if we're not unzipping
            if not self.unzip and not to_patch_rom:
                for o in short_out_files:

                    if final_file_exists:
                        continue

                    if o == rom:
                        final_file_exists = True

            # If we're unzipping (and potentially patching), then pull the expected files out here and check again
            if self.unzip or expecting_patched_rom:

                # Pull potential file extensions out
                file_exts = self.platform_config.get("file_exts", [])
                if len(file_exts) == 0:
                    raise ValueError(
                        "ROM file extensions should be defined in the platform config"
                    )

                rom_no_ext = os.path.splitext(rom)[0]

                # Add in that this has been patched, if necessary
                if expecting_patched_rom:
                    rom_no_ext += " (ROMPatched)"

                # Loop over the files, loop over the ROM file extensions, look for a match
                for o in short_out_files:
                    for file_ext in file_exts:
                        rom_w_ext = rom_no_ext + file_ext

                        if o == rom_w_ext:
                            final_file_exists = True

            # If nothing has changed, then move on
            if rom_dict[rom]["file_mod_time"] == cache_mod_time and final_file_exists:
                self.logger.info(
                    centred_string(
                        f"No updates for {rom}, skipping",
                        total_length=self.log_line_length,
                    )
                )

                # Gracefully update the cache from earlier versions
                cache_files = (
                    self.cache.get(self.platform, {})
                    .get(self.game, {})
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
                        rom=rom,
                        files=short_out_files,
                        out_dir=dir_name,
                        rom_dict=rom_dict,
                    )

                continue

            # We need to keep track of output files
            out_files = []

            # If we're patching ROMs, then do that here
            if to_patch_rom:

                rom_file = os.path.join(self.raw_dir, self.platform, rom)

                patcher = ROMPatcher(
                    platform=self.platform,
                    config=self.config,
                    logger=self.logger,
                    log_line_length=self.log_line_length,
                )

                full_rom = patcher.run(
                    file=rom_file,
                    patch_url=patch_url,
                )

                unzip = False
                patched = True

            else:
                full_dir = os.path.join(self.raw_dir, self.platform)
                full_rom = os.path.join(str(full_dir), rom)
                unzip = copy.deepcopy(self.unzip)

                patched = False

            # Log whether we've patched or not
            rom_dict[rom]["patched"] = patched

            # Move the main file. Don't delete folders as the game and the out directory
            # don't necessarily match
            move_file_success, moved_files = self.move_file(
                full_rom, out_dir=out_dir, unzip=unzip
            )

            if not move_file_success:
                self.logger.warning(
                    centred_string(
                        f"{rom} not found in raw directory, skipping",
                        total_length=self.log_line_length,
                    )
                )
                continue

            out_files.extend(moved_files)

            self.logger.info(
                centred_string(f"Moved {rom}", total_length=self.log_line_length)
            )

            # If there are additional file to move/unzip, do that now
            if "additional_dirs" in self.platform_config:
                for add_dir in self.platform_config["additional_dirs"]:

                    add_full_dir = f"{self.raw_dir} {add_dir}"
                    add_file = os.path.join(add_full_dir, rom)
                    if os.path.exists(add_file):
                        move_file_success, moved_files = self.move_file(
                            add_file, unzip=self.unzip
                        )

                        if not move_file_success:
                            self.logger.warning(
                                centred_string(
                                    f"{rom} {add_dir} not found in raw directory, skipping",
                                    total_length=self.log_line_length,
                                )
                            )
                        else:
                            self.logger.info(
                                centred_string(
                                    f"Moved {rom} {add_dir}",
                                    total_length=self.log_line_length,
                                )
                            )
                            out_files.extend(moved_files)

            # Update the cache
            self.cache_update(
                rom=rom, files=out_files, out_dir=dir_name, rom_dict=rom_dict
            )

            roms_moved.append(rom)

        return roms_moved

    def move_file(
        self,
        zip_file_name,
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
            out_dir = os.path.join(self.rom_dir, self.platform, self.game)

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

    def cache_update(
        self,
        rom,
        files,
        out_dir,
        rom_dict,
    ):
        """Update the cache with new file data

        Args:
            rom: ROM name to save to cache
            files: List of files to save to cache
            out_dir: Output directory for files, relative to [rom_dir]/[platform]
            rom_dict: Dictionary of ROM properties
        """

        if self.platform not in self.cache:
            self.cache[self.platform] = {}

        if self.game not in self.cache[self.platform]:
            self.cache[self.platform][self.game] = {}

        # If there's already something in there, clear it out
        if not self.cache[self.platform][self.game]:
            self.cache[self.platform][self.game] = {}

        # Include info about whether the ROM has been patched or not,
        # the patch file, and all the files we've included and where
        # we've put em

        self.cache[self.platform][self.game][rom] = {
            "file_mod_time": rom_dict[rom]["file_mod_time"],
            "patch_file": rom_dict[rom]["patch_file"],
            "patched": rom_dict[rom]["patched"],
            "output_directory": out_dir,
            "all_files": files,
        }

    def save_cache(self):
        """Save out the cache file"""

        cache = copy.deepcopy(self.cache)
        save_json(cache, self.cache_file, sort_key=self.platform)
