import glob
import os

import romsearch
from .datparser import DATParser
from .dupeparser import DupeParser
from .gamefinder import GameFinder
from .romchooser import ROMChooser
from .romdownloader import ROMDownloader
from .rommover import ROMMover
from .romparser import ROMParser
from ..util import (load_yml,
                    setup_logger,
                    create_bar,
                    discord_push,
                    split,
                    get_short_name,
                    )


class ROMSearch:

    def __init__(self,
                 config_file=None,
                 config=None,
                 default_config=None,
                 regex_config=None,
                 ):
        """General search tool to get ROMs downloaded and organized into files

        Args:
            config_file (str, optional): path to config file. Defaults to None.
            config (dict, optional): configuration dictionary. Defaults to None.
            default_config (dict, optional): default configuration dictionary. Defaults to None.
            regex_config (dict, optional): regex configuration dictionary. Defaults to None.
        """

        if config_file is None and config is None:
            raise ValueError("config_file or config must be specified")

        if config is None:
            config = load_yml(config_file)
        self.config = config

        self.logger = setup_logger("info", "ROMSearch")

        # Read in the various pre-set configs we've got
        self.mod_dir = os.path.dirname(romsearch.__file__)

        if default_config is None:
            default_file = os.path.join(self.mod_dir, "configs", "defaults.yml")
            default_config = load_yml(default_file)
        self.default_config = default_config

        if regex_config is None:
            regex_file = os.path.join(self.mod_dir, "configs", "regex.yml")
            regex_config = load_yml(regex_file)
        self.regex_config = regex_config

        # Pull in variables from the yaml file
        self.raw_dir = self.config.get("raw_dir", None)
        if self.raw_dir is None:
            raise ValueError("raw_dir needs to be defined in config")

        self.rom_dir = self.config.get("rom_dir", None)
        if self.rom_dir is None:
            raise ValueError("rom_dir needs to be defined in config")

        # Pull out platforms, make sure they're all valid
        platforms = self.config.get("platforms", None)
        if platforms is None:
            platforms = []
        if isinstance(platforms, str):
            platforms = [platforms]
        for platform in platforms:
            if platform not in self.default_config["platforms"]:
                raise ValueError(f"Platforms should be any of {self.default_config['platforms']}, not {platform}")
        self.platforms = platforms

        # Which modules to run
        self.run_romdownloader = self.config.get("run_romdownloader", True)
        self.run_datparser = self.config.get("run_datparser", True)
        self.run_dupeparser = self.config.get("run_dupeparser", True)
        self.run_romchooser = self.config.get("run_romchooser", True)
        self.run_rommover = self.config.get("run_rommover", True)

        # Finally, the discord URL if we're sending messages
        self.discord_url = self.config.get("discord", {}).get("webhook_url", None)

        self.dry_run = self.config.get("romsearch", {}).get("dry_run", False)

    def run(self):
        """Run ROMSearch"""

        self.logger.info(create_bar(f"START ROMSearch"))

        self.logger.info(f"Looping over platforms: {self.platforms}")

        all_roms_per_platform = {}

        for platform in self.platforms:

            self.logger.info(f"Running ROMSearch for {platform}")

            # Pull in platform-specific config
            platform_config_file = os.path.join(self.mod_dir, "configs", "platforms", f"{platform}.yml")
            platform_config = load_yml(platform_config_file)

            raw_dir = os.path.join(self.raw_dir, platform)

            # Run the rclone sync
            if self.run_romdownloader:
                downloader = ROMDownloader(platform=platform,
                                           config=self.config,
                                           platform_config=platform_config,
                                           )
                downloader.run()

            # Get the original directory, so we can safely move back after
            orig_dir = os.getcwd()
            os.chdir(raw_dir)

            all_files = glob.glob("*.zip")
            all_files.sort()

            # Parse this into a dictionary with some useful info for each file
            all_file_dict = {}
            for f in all_files:
                short_name = get_short_name(f,
                                            regex_config=self.regex_config,
                                            default_config=self.default_config,
                                            )

                all_file_dict[f] = {
                    "short_name": short_name,
                    "matched": False,
                }

            os.chdir(orig_dir)

            # Parse DAT files here, if we're doing that
            if self.run_datparser:
                dat_parser = DATParser(platform=platform,
                                       config=self.config,
                                       platform_config=platform_config,
                                       )
                dat_parser.run()

            # Get dupes here, if we're doing that
            if self.run_dupeparser:
                dupe_parser = DupeParser(platform=platform,
                                         config=self.config,
                                         default_config=self.default_config,
                                         regex_config=self.regex_config,
                                         )
                dupe_parser.run()

            # Find files
            finder = GameFinder(platform=platform,
                                config=self.config,
                                default_config=self.default_config,
                                regex_config=self.regex_config,
                                )

            all_games = finder.run(files=all_file_dict)
            self.logger.info(f"Searching through {len(all_games)} games")

            all_roms_moved = []

            for i, game in enumerate(all_games):

                self.logger.info(f"{i + 1}/{len(all_games)}: {game} (aliases {', '.join(all_games[game])}):")

                # Parse by the short name, include the priority in there as well
                rom_files = {}

                games_lower = [g.lower() for g in all_games[game]]
                priorities = [all_games[game][g]["priority"] for g in all_games[game]]
                for f in all_file_dict:
                    file_short_name_lower = all_file_dict[f]["short_name"].lower()
                    if file_short_name_lower in games_lower:
                        games_idx = games_lower.index(file_short_name_lower)
                        rom_files[f] = {
                            "priority": priorities[games_idx],
                        }

                        if all_file_dict[f]["matched"]:
                            raise ValueError(f"{f} has already been matched! This should not happen")

                        all_file_dict[f]["matched"] = True

                parse = ROMParser(platform=platform,
                                  game=game,
                                  config=self.config,
                                  platform_config=platform_config,
                                  regex_config=self.regex_config,
                                  default_config=self.default_config,
                                  )
                rom_dict = parse.run(rom_files)

                if self.run_romchooser:
                    # Here, we'll parse down the number of files to one game, one ROM
                    chooser = ROMChooser(platform=platform,
                                         game=game,
                                         config=self.config,
                                         regex_config=self.regex_config,
                                         default_config=self.default_config,
                                         )
                    rom_dict = chooser.run(rom_dict)

                if len(rom_dict) == 0:
                    self.logger.info(f"All files filtered. Skipping")
                    continue

                # Print out all the ROMs we've now matched
                rom_files = [f for f in rom_dict]
                self.logger.info(f"Found ROM file(s): {rom_files}")

                if self.dry_run:
                    self.logger.info("Dry run, will not move any files")
                    continue

                if not self.run_rommover:
                    self.logger.debug("ROMMover is not running, will not move anything")
                    continue

                mover = ROMMover(platform=platform,
                                 game=game,
                                 config=self.config,
                                 platform_config=platform_config
                                 )
                roms_moved = mover.run(rom_dict)
                all_roms_moved.extend(roms_moved)

            if len(all_roms_moved) > 0:
                all_roms_per_platform[platform] = all_roms_moved

            # Post these to Discord in chunks of 10
            if self.discord_url is not None and len(all_roms_moved) > 0:

                for items_split in split(all_roms_moved):

                    fields = []

                    field_dict = {"name": platform,
                                  "value": "\n".join(items_split)
                                  }
                    fields.append(field_dict)

                    if len(fields) > 0:
                        discord_push(url=self.discord_url,
                                     name="ROMSearch",
                                     fields=fields,
                                     )

            for f in all_file_dict:
                if not all_file_dict[f]["matched"]:
                    self.logger.warning(f"{f} not matched to anything")

        self.logger.info(create_bar(f"FINISH ROMSearch"))

        return True
