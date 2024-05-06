import copy
import os
import shutil

import romsearch
from ..util import load_yml, setup_logger, create_bar, unzip_file, load_json, save_json


class ROMMover:

    def __init__(self,
                 config_file,
                 platform,
                 game
                 ):
        """ROM Moving and cache updating tool

        Because we do this per-platform, per-game, they need to be specified here
        """

        logger_add_dir = str(os.path.join(platform, game))

        self.logger = setup_logger(log_level="info",
                                   script_name=f"ROMMover",
                                   additional_dir=logger_add_dir,
                                   )

        config = load_yml(config_file)

        self.raw_dir = config.get("raw_dir", None)
        if self.raw_dir is None:
            raise ValueError("raw_dir needs to be defined in config")

        self.rom_dir = config.get("rom_dir", None)
        if self.rom_dir is None:
            raise ValueError("rom_dir needs to be defined in config")

        cache_file = config.get("rommover", {}).get("cache_file", None)
        if cache_file is None:
            cache_file = os.path.join(os.getcwd(), f"cache ({platform}).json")

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
        platform_config_file = os.path.join(mod_dir, "configs", "platforms", f"{platform}.yml")
        platform_config = load_yml(platform_config_file)

        self.platform_config = platform_config
        self.unzip = self.platform_config.get("unzip", False)

    def run(self,
            rom_dict,
            ):

        self.logger.info(create_bar(f"START ROMMover"))

        roms_moved = self.move_roms(rom_dict)
        self.save_cache()

        self.logger.info(create_bar(f"FINISH ROMMover"))

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
                self.logger.info(f"No updates for {rom}, skipping")
                continue

            if rom_no == 0:
                delete_folder = True
            else:
                delete_folder = False

            # Move the main file
            full_dir = os.path.join(self.raw_dir, self.platform)
            full_rom = os.path.join(str(full_dir), rom)
            self.move_file(full_rom, unzip=self.unzip, delete_folder=delete_folder)
            self.logger.info(f"Moved {rom}")

            # If there are additional file to move/unzip, do that now
            if "additional_dirs" in self.platform_config:
                for add_dir in self.platform_config["additional_dirs"]:

                    add_full_dir = f"{self.raw_dir} {add_dir}"
                    add_file = os.path.join(add_full_dir, rom)
                    if os.path.exists(add_file):
                        self.move_file(add_file, unzip=self.unzip)
                        self.logger.info(f"Moved {rom} {add_dir}")

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
