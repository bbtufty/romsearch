import copy
import os
import shutil

import romsearch
from ..util import (centred_string,
                    load_yml,
                    setup_logger,
                    unzip_file,
                    load_json,
                    save_json
                    )


class ROMMover:

    def __init__(self,
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
            log_dir = self.config.get("dirs", {}).get("log_dir", os.path.join(os.getcwd(), "logs"))
            logger_add_dir = str(os.path.join(platform, game))
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(log_level=log_level,
                                  script_name=f"ROMMover",
                                  log_dir=log_dir,
                                  additional_dir=logger_add_dir,
                                  )
        self.logger = logger

        self.raw_dir = self.config.get("dirs", {}).get("raw_dir", None)
        if self.raw_dir is None:
            raise ValueError("raw_dir needs to be defined in config")

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
        self.game = game
        self.cache_file = cache_file
        self.cache = cache

        # Pull in platform config that we need
        mod_dir = os.path.dirname(romsearch.__file__)

        if platform_config is None:
            platform_config_file = os.path.join(mod_dir, "configs", "platforms", f"{platform}.yml")
            platform_config = load_yml(platform_config_file)
        self.platform_config = platform_config

        self.unzip = self.platform_config.get("unzip", False)

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(self,
            rom_dict,
            ):

        roms_moved = self.move_roms(rom_dict)
        self.save_cache()

        return roms_moved

    def move_roms(self, rom_dict):
        """Actually move the roms"""

        roms_moved = []

        for rom_no, rom in enumerate(rom_dict):

            cache_mod_time = (self.cache.get(self.platform, {}).
                              get(self.game, {}).
                              get(rom, {}).
                              get("file_mod_time", 0)
                              )

            if rom_dict[rom]["file_mod_time"] == cache_mod_time:
                self.logger.info(centred_string(f"No updates for {rom}, skipping",
                                                total_length=self.log_line_length)
                                 )
                continue

            if rom_no == 0:
                delete_folder = True
            else:
                delete_folder = False

            # Move the main file
            full_dir = os.path.join(self.raw_dir, self.platform)
            full_rom = os.path.join(str(full_dir), rom)
            self.move_file(full_rom, unzip=self.unzip, delete_folder=delete_folder)
            self.logger.info(centred_string(f"Moved {rom}",
                                            total_length=self.log_line_length)
                             )

            # If there are additional file to move/unzip, do that now
            if "additional_dirs" in self.platform_config:
                for add_dir in self.platform_config["additional_dirs"]:

                    add_full_dir = f"{self.raw_dir} {add_dir}"
                    add_file = os.path.join(add_full_dir, rom)
                    if os.path.exists(add_file):
                        self.move_file(add_file, unzip=self.unzip)
                        self.logger.info(centred_string(f"Moved {rom} {add_dir}",
                                                        total_length=self.log_line_length)
                                         )

            # Update the cache
            self.cache_update(file=rom, rom_dict=rom_dict)

            roms_moved.append(rom)

        return roms_moved

    def move_file(self,
                  zip_file_name,
                  unzip=False,
                  delete_folder=False,
                  ):
        """Move file to directory structure, optionally unzipping"""

        out_dir = os.path.join(self.rom_dir, self.platform, self.game)

        if delete_folder and os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_dir = str(out_dir)

        if unzip:
            unzip_file(zip_file_name, out_dir)
        else:
            short_zip_file = os.path.split(zip_file_name)[-1]
            out_file = os.path.join(out_dir, short_zip_file)

            # Remove this file if it already exists
            if os.path.exists(out_file):
                os.remove(out_file)

            os.link(zip_file_name, out_file)

        return True

    def cache_update(self, file, rom_dict):
        """Update the cache with new file data"""

        if self.platform not in self.cache:
            self.cache[self.platform] = {}

        if self.game not in self.cache[self.platform]:
            self.cache[self.platform][self.game] = {}

        # If there's already something in there, clear it out
        if not self.cache[self.platform][self.game]:
            self.cache[self.platform][self.game] = {}

        self.cache[self.platform][self.game][file] = {"file_mod_time": rom_dict[file]["file_mod_time"]}

    def save_cache(self):
        """Save out the cache file"""

        cache = copy.deepcopy(self.cache)
        save_json(cache, self.cache_file)
