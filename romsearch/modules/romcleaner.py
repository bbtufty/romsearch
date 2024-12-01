import copy
import glob
import os
import shutil

import romsearch
from ..util import (
    centred_string,
    load_yml,
    setup_logger,
    load_json,
    save_json, )


class ROMCleaner:

    def __init__(
        self,
        platform,
        config_file=None,
        config=None,
        platform_config=None,
        logger=None,
        log_line_sep="=",
        log_line_length=100,
    ):
        """ROM directory cleaner

        Cleans out ROMs we no longer want in the final ROM directory

        Args:
            platform (str): Platform name
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
            logger_add_dir = copy.deepcopy(platform)
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(
                log_level=log_level,
                script_name=f"ROMCleaner",
                log_dir=log_dir,
                additional_dir=logger_add_dir,
            )
        self.logger = logger

        self.rom_dir = self.config.get("dirs", {}).get("rom_dir", None)
        if self.rom_dir is None:
            raise ValueError("rom_dir needs to be defined in config")

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

        self.unzip = self.platform_config.get("unzip", False)

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(
        self,
        rom_dict,
    ):
        """Run the ROMCleaner

        Args:
            rom_dict (dict): Dictionary of ROMs we want to keep
        """

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")
        self.logger.info(
            centred_string("Running ROMCleaner", total_length=self.log_line_length)
        )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        roms_cleaned = self.clean_roms(rom_dict)
        self.save_cache()

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        return roms_cleaned

    def clean_roms(
        self,
        rom_dict,
    ):
        """Check in directory for any ROMs we don't want any more, and delete them

        Args:
            rom_dict (dict): Dictionary of ROMs we want to keep
        """

        full_rom_dir = os.path.join(self.rom_dir, self.platform)

        # Find files on disk
        roms_on_disk = glob.glob(os.path.join(full_rom_dir, "*", "*.*"))

        # Pull out any included ROMs, stripping out the extension
        roms_in_dict = {}
        for r in rom_dict:

            for f in rom_dict[r]:
                if rom_dict[r][f]["excluded"]:
                    continue
                rom_name = os.path.splitext(f)[0]

                # We need to include if things have been patched. Pull that from the cache
                patched = (
                    self.cache.get(self.platform, {})
                    .get(r, {})
                    .get(f, {})
                    .get("patched", False)
                )
                if patched:
                    rom_name += " (ROMPatched)"

                roms_in_dict[rom_name] = {"full_name": f}

        roms_cleaned = []
        dict_cleaned = {}

        for rom_on_disk in roms_on_disk:

            # Pull out a short ROM name, skipping any extensions and parent directories
            rom_short = os.path.split(rom_on_disk)[-1]
            rom_short = os.path.splitext(rom_short)[0]

            # Loop over, see if we can find the ROM
            found_rom_in_dict = False
            for r in roms_in_dict:

                if found_rom_in_dict:
                    continue

                if r == rom_short:
                    found_rom_in_dict = True

            # If we haven't found anything, clear out the cache
            if not found_rom_in_dict:

                # Just loop through the dictionary
                found_entry_in_dict = False
                if self.platform in self.cache:

                    for g in self.cache[self.platform]:

                        if found_entry_in_dict:
                            continue

                        for g_i in self.cache[self.platform][g]:

                            if found_entry_in_dict:
                                continue

                            g_i_short = os.path.splitext(g_i)[0]

                            if g_i_short == rom_short:

                                # Also keep info on the dictionary stuff to clean from the cache
                                if g not in dict_cleaned:
                                    dict_cleaned[g] = []
                                dict_cleaned[g].append(g_i)

                                # Remove from the filesystem
                                found_entry_in_dict = True
                                roms_cleaned.append(rom_short)
                                os.remove(rom_on_disk)
                                self.logger.info(
                                    centred_string(
                                        f"Removed {rom_short} from disk", total_length=self.log_line_length
                                    )
                                )

        # Now pass through, removing items we no longer need and keeping track
        # of empty cache items
        cache_items_to_pop = []
        if self.platform in self.cache:
            for d in dict_cleaned:
                for d_i in dict_cleaned[d]:
                    self.cache[self.platform][d].pop(d_i, None)
                    if len(self.cache[self.platform][d]) == 0:
                        cache_items_to_pop.append(d)

        # Go through all the cache entries and if we no longer have them on disk, clear those out
        if self.platform in self.cache:
            for d in self.cache[self.platform]:

                d_is_to_remove = []
                for d_i in self.cache[self.platform][d]:
                    found_d_i_on_disk = False

                    d_i_short = os.path.splitext(d_i)[0]

                    # Account for the fact the file might be patched
                    if self.cache[self.platform][d][d_i]["patched"]:
                        d_i_short += " (ROMPatched)"

                    for r in roms_on_disk:

                        if found_d_i_on_disk:
                            continue

                        r_base = os.path.basename(r)
                        r_short = os.path.splitext(r_base)[0]
                        if r_short == d_i_short:
                            found_d_i_on_disk = True

                    if not found_d_i_on_disk:
                        d_is_to_remove.append(d_i)

                for d_i_to_remove in d_is_to_remove:
                    self.cache[self.platform][d].pop(d_i_to_remove, None)

                    self.logger.info(
                        centred_string(
                            f"Removed {d_i_to_remove} from cache", total_length=self.log_line_length
                        )
                    )

                    if len(self.cache[self.platform][d]) == 0:
                        cache_items_to_pop.append(d)

        # Clear out any empty cache items
        if self.platform in self.cache:
            for d in cache_items_to_pop:
                self.cache[self.platform].pop(d, None)

                self.logger.info(
                    centred_string(
                        f"Removed {d} from cache", total_length=self.log_line_length
                    )
                )

        # Remove any empty directories
        all_dirs = os.listdir(full_rom_dir)
        for d in all_dirs:
            full_dir = os.path.join(full_rom_dir, d)
            if not os.listdir(full_dir):
                shutil.rmtree(full_dir)

        return roms_cleaned

    def save_cache(self):
        """Save out the cache file"""

        cache = copy.deepcopy(self.cache)
        save_json(cache, self.cache_file, sort_key=self.platform)
