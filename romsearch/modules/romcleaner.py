import copy
import fnmatch
import glob
import numpy as np
import os
import shutil

import romsearch
from ..util import (
    centred_string,
    load_yml,
    setup_logger,
    load_json,
    save_json,
)


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

        # Whether we'll handle multi-disc files or not
        self.handle_multi_discs = self.config.get("romsearch", {}).get(
            "handle_multi_discs", False
        )

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

        roms_cleaned, cache_cleaned = self.clean_roms(rom_dict)
        self.save_cache()

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        # Join these up into a dictionary
        cleaned = {
            "ROMs": roms_cleaned,
            "Cache": cache_cleaned,
        }

        return cleaned

    def clean_roms(
        self,
        rom_dict,
    ):
        """Check in the directory for any ROMs we don't want any more and delete them

        Args:
            rom_dict (dict): Dictionary of ROMs we want to keep
        """

        full_rom_dir = os.path.join(self.rom_dir, self.platform)

        roms_cleaned = []
        cache_cleaned = []
        dict_cleaned = {}

        # Find files in the cache that are no longer included
        if self.platform in self.cache:
            for r in self.cache[self.platform]:
                for f in self.cache[self.platform][r]:

                    is_multi_disc = self.cache[self.platform][r][f].get(
                        "multi_disc", False
                    )

                    if not is_multi_disc:
                        # Get whether we've excluded or not. If we don't have it in the ROM dict, exclude to start
                        excluded = rom_dict.get(r, {}).get(f, {}).get("excluded", True)

                        # If we're not excluded, double-check that it's not a superset or compilation that might
                        # be hanging around
                        if not excluded:
                            f_superset = rom_dict.get(r, {}).get(f, {}).get("is_superset", False)
                            f_compilation = rom_dict.get(r, {}).get(f, {}).get("is_compilation", False)

                            # If it is a superset or compilation, then exclude if the short name doesn't match
                            # the directory name

                            if f_superset or f_compilation:
                                f_short = rom_dict.get(r, {}).get(f, {}).get("short_name", r)
                                if f_short != r:
                                    excluded = True

                        # If something has been excluded, but it is an included compilation/superset, then don't exclude
                        if excluded:

                            truly_excluded = copy.deepcopy(excluded)

                            for rr in rom_dict:

                                if not truly_excluded:
                                    continue

                                if f in rom_dict[rr].keys():

                                    f_superset = rom_dict[rr][f].get("is_superset", False)
                                    f_compilation = rom_dict[rr][f].get("is_compilation", False)
                                    f_excluded = rom_dict[rr][f].get("excluded", True)

                                    # Also, check the directory name against the short name here
                                    f_short = rom_dict[rr][f]["short_name"]

                                    if (f_superset or f_compilation) and not f_excluded and f_short == r:
                                        truly_excluded = False

                            excluded = copy.deepcopy(truly_excluded)

                    else:

                        # If we've got a multi-disc file, but we're not supposed to have them, then exclude
                        excluded = True
                        if self.handle_multi_discs:
                            excluded = False

                    # If we've excluded the file, we want to delete it here both from the cache and on disk
                    if excluded:
                        if r not in dict_cleaned:
                            dict_cleaned[r] = []
                        dict_cleaned[r].append(f)

        # Find items in the cache that aren't on disk
        if self.platform in self.cache:
            for r in self.cache[self.platform]:
                for f in self.cache[self.platform][r]:

                    # Just check if any files exist to speed things up
                    files_exist = False

                    # If we don't have an output directory, we should clear this from the cache
                    rom_output_directory = self.cache[self.platform][r][f].get(
                        "output_directory", None
                    )
                    if rom_output_directory is None:
                        dict_cleaned[r].append(f)
                        continue

                    for rom_file in self.cache[self.platform][r][f]["all_files"]:
                        rom_output_file = os.path.join(
                            full_rom_dir, rom_output_directory, rom_file
                        )

                        if os.path.exists(rom_output_file):
                            files_exist = True

                        if files_exist:
                            continue

                    if not files_exist:
                        if r not in dict_cleaned:
                            dict_cleaned[r] = []
                        dict_cleaned[r].append(f)

        # Now pass through, removing items we no longer need and keeping track
        # of empty cache items
        cache_items_to_pop = []
        if self.platform in self.cache:
            for d in dict_cleaned:
                for d_i in dict_cleaned[d]:
                    self.cache[self.platform][d].pop(d_i, None)
                    if len(self.cache[self.platform][d]) == 0:
                        cache_items_to_pop.append(d)

        cache_items_to_pop = np.unique(cache_items_to_pop)
        cache_items_to_pop = [str(f) for f in cache_items_to_pop]

        # Clear out any empty cache items
        if self.platform in self.cache:
            for d in cache_items_to_pop:

                cache_cleaned.append(d)
                self.cache[self.platform].pop(d, None)
                self.logger.info(
                    centred_string(
                        f"Removed {d} from cache", total_length=self.log_line_length
                    )
                )

        # Find files on disk, searching recursively
        roms_on_disk = glob.glob(
            os.path.join(full_rom_dir, "*/", "*.*"), recursive=True
        )

        # Clear out files that are not in the cache
        roms_in_cache = []
        if self.platform in self.cache:
            for r in self.cache[self.platform]:

                for f in self.cache[self.platform][r]:

                    rom_output_directory = copy.deepcopy(
                        self.cache[self.platform][r][f]["output_directory"]
                    )

                    for rom_file in self.cache[self.platform][r][f]["all_files"]:
                        rom_file_w_directory = os.path.join(
                            full_rom_dir, rom_output_directory, rom_file
                        )
                        roms_in_cache.append(rom_file_w_directory)

        for r in roms_on_disk:

            found_rom_in_cache = False

            for c in roms_in_cache:

                if found_rom_in_cache:
                    continue

                if fnmatch.fnmatchcase(r, c):
                    found_rom_in_cache = True

            if not found_rom_in_cache:
                r_short = os.path.basename(r)
                os.remove(r)
                roms_cleaned.append(r_short)

        # Remove any empty directories, searching recursively
        for root, subdirs, _ in os.walk(full_rom_dir):

            if len(subdirs) > 0:
                for subdir in subdirs:
                    full_dir = os.path.join(root, subdir)
                    if not os.listdir(full_dir):
                        shutil.rmtree(full_dir)

        # Because there can be some duplicates, remove here
        roms_cleaned = np.unique(roms_cleaned)
        roms_cleaned = [str(f) for f in roms_cleaned]

        cache_cleaned = np.unique(cache_cleaned)
        cache_cleaned = [str(f) for f in cache_cleaned]

        return roms_cleaned, cache_cleaned

    def save_cache(self):
        """Save out the cache file"""

        cache = copy.deepcopy(self.cache)
        save_json(cache, self.cache_file, sort_key=self.platform)
