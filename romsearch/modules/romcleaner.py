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
        roms_in_dict = []
        for r in rom_dict:
            included_roms = [
                os.path.splitext(f)[0]
                for f in rom_dict[r]
                if rom_dict[r][f]["excluded"] == False
            ]
            roms_in_dict.extend(included_roms)

        roms_cleaned = []

        for rom_on_disk in roms_on_disk:

            # Pull out a short ROM name, skipping any extensions and parent directories
            rom_short = os.path.split(rom_on_disk)[-1]
            rom_short = os.path.splitext(rom_short)[0]

            if rom_short not in roms_in_dict:

                # Delete the file
                os.remove(rom_on_disk)
                parent_dir = os.path.split(os.path.dirname(rom_on_disk))[-1]
                if self.platform in self.cache:
                    self.cache[self.platform].pop(parent_dir, None)

                roms_cleaned.append(rom_short)

                self.logger.info(
                    centred_string(
                        f"Removed {rom_short}", total_length=self.log_line_length
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
        save_json(cache, self.cache_file)
