import glob
import os
import time

import numpy as np

import romsearch
from .datparser import DATParser
from .dupeparser import DupeParser
from .gamefinder import GameFinder
from .rahasher import RAHasher
from .romchooser import ROMChooser
from .romcleaner import ROMCleaner
from .romdownloader import ROMDownloader
from .rommover import ROMMover
from .romparser import ROMParser
from ..util import (
    centred_string,
    load_yml,
    setup_logger,
    discord_push,
    split,
    get_short_name,
    get_region_free_name,
    normalize_name,
    get_file_time,
    get_directory_name,
)

ALLOWED_ROMSEARCH_METHODS = [
    "filter_then_download",
    "download_then_filter",
]


class ROMSearch:

    def __init__(
        self,
        config_file=None,
        config=None,
        default_config=None,
        regex_config=None,
        logger=None,
    ):
        """General search tool to get ROMs downloaded and organized into files

        Args:
            config_file (str, optional): path to config file. Defaults to None.
            config (dict, optional): configuration dictionary. Defaults to None.
            default_config (dict, optional): default configuration dictionary. Defaults to None.
            regex_config (dict, optional): regex configuration dictionary. Defaults to None.

        TODO:
            - More granular control over compilations
        """

        if config_file is None and config is None:
            raise ValueError("config_file or config must be specified")

        if config is None:
            config = load_yml(config_file)
        self.config = config

        # Pull in directories from the yaml file
        self.raw_dir = self.config.get("dirs", {}).get("raw_dir", None)
        if self.raw_dir is None:
            raise ValueError("raw_dir needs to be defined in config")

        self.rom_dir = self.config.get("dirs", {}).get("rom_dir", None)
        if self.rom_dir is None:
            raise ValueError("rom_dir needs to be defined in config")

        if logger is None:
            log_dir = self.config.get("dirs", {}).get(
                "log_dir", os.path.join(os.getcwd(), "logs")
            )
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(
                log_level=log_level,
                script_name="ROMSearch",
                log_dir=log_dir,
            )
        self.logger = logger

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

        # Pull out platforms, make sure they're all valid
        platforms = self.config.get("platforms", None)
        if platforms is None:
            platforms = []
        if isinstance(platforms, str):
            platforms = [platforms]
        for platform in platforms:
            if platform not in self.default_config["platforms"]:
                raise ValueError(
                    f"Platforms should be any of {self.default_config['platforms']}, not {platform}"
                )
        self.platforms = platforms

        self.romsearch_method = self.config.get("romsearch", {}).get(
            "method", "filter_then_download"
        )

        # Which modules to run
        self.run_romdownloader = self.config.get("romsearch", {}).get(
            "run_romdownloader", True
        )
        self.run_rahasher = self.config.get("romsearch", {}).get("run_rahasher", False)
        self.run_datparser = self.config.get("romsearch", {}).get("run_datparser", True)
        self.run_dupeparser = self.config.get("romsearch", {}).get(
            "run_dupeparser", True
        )
        self.run_romchooser = self.config.get("romsearch", {}).get(
            "run_romchooser", True
        )
        self.run_rommover = self.config.get("romsearch", {}).get("run_rommover", True)
        self.dry_run = self.config.get("romsearch", {}).get("dry_run", False)

        # Finally, the discord URL if we're sending messages
        self.discord_url = self.config.get("discord", {}).get("webhook_url", None)

    def run(
        self,
        log_line_sep="=",
        log_line_length=100,
    ):
        """Run ROMSearch

        Args:
            log_line_sep (str, optional): log line separator. Defaults to "=".
            log_line_length (int, optional): log line length. Defaults to 100.
        """

        start = time.time()

        # Log some useful info
        self.logger.info(f"{log_line_sep * log_line_length}")
        self.logger.info(
            centred_string("Running ROMSearch for:", total_length=log_line_length)
        )
        self.logger.info(f"{'-' * log_line_length}")
        for platform in self.platforms:
            self.logger.info(centred_string(platform, total_length=log_line_length))
        self.logger.info(f"{log_line_sep * log_line_length}")

        for platform in self.platforms:

            self.logger.info(f"{log_line_sep * log_line_length}")
            self.logger.info(
                centred_string(f"Beginning {platform}", total_length=log_line_length)
            )
            self.logger.info(f"{log_line_sep * log_line_length}")

            # Pull in platform-specific config
            platform_config_file = os.path.join(
                self.mod_dir, "configs", "platforms", f"{platform}.yml"
            )
            platform_config = load_yml(platform_config_file)

            raw_dir = os.path.join(self.raw_dir, platform)

            # Parse the RA hashes here, if we're doing that
            ra_hash_dict = None
            if self.run_rahasher:
                ra_hasher = RAHasher(
                    platform=platform,
                    config=self.config,
                    logger=self.logger,
                    log_line_length=log_line_length,
                )
                ra_hash_dict = ra_hasher.run()

            # Parse DAT files here, if we're doing that
            dat_dict = None
            if self.run_datparser:
                dat_parser = DATParser(
                    platform=platform,
                    config=self.config,
                    platform_config=platform_config,
                    logger=self.logger,
                    log_line_length=log_line_length,
                )
                dat_dict = dat_parser.run()

            # Get dupes here, if we're doing that
            dupe_dict = None
            retool_dict = None
            if self.run_dupeparser:
                dupe_parser = DupeParser(
                    platform=platform,
                    config=self.config,
                    default_config=self.default_config,
                    regex_config=self.regex_config,
                    logger=self.logger,
                    log_line_length=log_line_length,
                )
                dupe_dict, retool_dict = dupe_parser.run()

            if self.romsearch_method == "download_then_filter":
                # Run the rclone sync
                if self.run_romdownloader:
                    downloader = ROMDownloader(
                        platform=platform,
                        config=self.config,
                        platform_config=platform_config,
                        logger=self.logger,
                        log_line_length=log_line_length,
                    )
                    downloader.run()

                # Get the original directory, so we can safely move back after
                orig_dir = os.getcwd()
                os.chdir(raw_dir)

                all_files = glob.glob("*.zip")
                all_files.sort()

                os.chdir(orig_dir)

            elif self.romsearch_method == "filter_then_download":

                if not self.run_datparser:
                    raise ValueError(
                        "If using filter, then download method, you must run DATParser"
                    )

                parsed_dat_dir = self.config.get("dirs", {}).get("parsed_dat_dir", None)
                if parsed_dat_dir is None:
                    raise ValueError("parsed_dat_dir needs to be defined in config")

                all_files = [f"{f}.zip" for f in dat_dict]
                all_files = np.unique(all_files)
                all_files = [str(f) for f in all_files]
                all_files.sort()

            else:

                raise ValueError(
                    f"ROMSearch method should be one of {ALLOWED_ROMSEARCH_METHODS}"
                )

            # Parse this into a dictionary with some useful info for each file
            all_file_dict = {}
            for f in all_files:

                dir_name = get_directory_name(f)
                full_name = normalize_name(
                    f,
                    disc_rename=self.default_config["disc_rename"],
                )
                short_name = get_short_name(
                    full_name,
                    regex_config=self.regex_config,
                    default_config=self.default_config,
                )
                region_free_name = get_region_free_name(
                    full_name,
                    regex_config=self.regex_config,
                    default_config=self.default_config,
                )

                all_file_dict[f] = {
                    "original_name": f,
                    "dir_name": dir_name,
                    "full_name": full_name,
                    "short_name": short_name,
                    "region_free_name": region_free_name,
                    "matched": False,
                }

            # Find files
            finder = GameFinder(
                platform=platform,
                config=self.config,
                dupe_dict=dupe_dict,
                default_config=self.default_config,
                regex_config=self.regex_config,
                logger=self.logger,
                log_line_length=log_line_length,
            )

            all_games = finder.run(files=all_file_dict)

            self.logger.info(f"{log_line_sep * log_line_length}")
            self.logger.info(
                centred_string(
                    f"Finding ROMs for {len(all_games)} game(s):",
                    total_length=log_line_length,
                )
            )
            self.logger.info(f"{'-' * log_line_length}")
            for g in all_games:
                self.logger.info(centred_string(g, total_length=log_line_length))
            self.logger.info(f"{log_line_sep * log_line_length}")

            all_roms_moved = []
            all_roms_dict = {}

            for game in all_games:

                rom_files = all_games[game]

                parse = ROMParser(
                    platform=platform,
                    game=game,
                    dat=dat_dict,
                    retool=retool_dict,
                    ra_hashes=ra_hash_dict,
                    config=self.config,
                    platform_config=platform_config,
                    regex_config=self.regex_config,
                    default_config=self.default_config,
                    logger=self.logger,
                    log_line_length=log_line_length,
                )
                rom_dict = parse.run(rom_files)

                if self.run_romchooser:
                    # Here, we'll parse down the number of files to one game, one ROM
                    chooser = ROMChooser(
                        platform=platform,
                        game=game,
                        config=self.config,
                        regex_config=self.regex_config,
                        default_config=self.default_config,
                        logger=self.logger,
                        log_line_length=log_line_length,
                    )
                    rom_dict = chooser.run(rom_dict)

                if len(rom_dict) == 0:
                    continue

                # Save to a big dictionary, since we'll move all at once
                all_roms_dict[game] = rom_dict

            if self.dry_run:
                self.logger.info(f"{log_line_sep * log_line_length}")
                self.logger.info(
                    centred_string(
                        "Dry run, will not move any files", total_length=log_line_length
                    )
                )
                self.logger.info(f"{log_line_sep * log_line_length}")
                continue

            if not self.run_rommover:
                self.logger.info(f"{log_line_sep * log_line_length}")
                self.logger.info(
                    centred_string(
                        "ROMMover is not running, will not move anything",
                        total_length=log_line_length,
                    )
                )
                self.logger.info(f"{log_line_sep * log_line_length}")
                continue

            # If we filter then download, this is where we download
            if self.romsearch_method == "filter_then_download":
                all_files = []
                for game in all_roms_dict:
                    fs = [f for f in all_roms_dict[game]]

                    all_files.extend(fs)

                if self.run_romdownloader:
                    downloader = ROMDownloader(
                        platform=platform,
                        config=self.config,
                        platform_config=platform_config,
                        logger=self.logger,
                        rclone_method="copy",
                        copy_files=all_files,
                        log_line_length=log_line_length,
                    )
                    downloader.run()

                # Replace the file time with the correct one on disk
                for game in all_roms_dict:

                    for f in all_roms_dict[game]:
                        full_filename = os.path.join(self.raw_dir, platform, f)

                        file_mod_time = get_file_time(
                            full_filename,
                            datetime_format=self.default_config["datetime_format"],
                        )
                        all_roms_dict[game][f]["file_mod_time"] = file_mod_time

            self.logger.info(f"{log_line_sep * log_line_length}")
            self.logger.info(
                centred_string("Running ROMMover", total_length=log_line_length)
            )
            self.logger.info(f"{log_line_sep * log_line_length}")

            for game in all_roms_dict:
                rom_dict = all_roms_dict[game]

                mover = ROMMover(
                    platform=platform,
                    game=game,
                    config=self.config,
                    platform_config=platform_config,
                    logger=self.logger,
                    log_line_length=log_line_length,
                )
                roms_moved = mover.run(rom_dict)
                all_roms_moved.extend(roms_moved)

            self.logger.info(f"{log_line_sep * log_line_length}")

            # Post these to Discord in chunks of 10
            if self.discord_url is not None and len(all_roms_moved) > 0:

                for items_split in split(all_roms_moved):

                    fields = []

                    field_dict = {"name": platform, "value": "\n".join(items_split)}
                    fields.append(field_dict)

                    if len(fields) > 0:
                        discord_push(
                            url=self.discord_url,
                            name="ROMSearch",
                            fields=fields,
                        )

            # Finally, clean up anything in the ROM directory that's been deleted
            cleaner = ROMCleaner(
                platform=platform,
                config=self.config,
                logger=self.logger,
                log_line_length=log_line_length,
            )
            cleaned = cleaner.run(all_roms_dict)

            # Post these to Discord in chunks of 10
            for c in cleaned:
                if self.discord_url is not None and len(cleaned[c]) > 0:

                    for items_split in split(cleaned[c]):

                        fields = []

                        field_dict = {"name": platform, "value": "\n".join(items_split)}
                        fields.append(field_dict)

                        if len(fields) > 0:
                            discord_push(
                                url=self.discord_url,
                                name=f"ROMCleaner [{c}]",
                                fields=fields,
                            )

            self.logger.info(f"{log_line_sep * log_line_length}")
            self.logger.info(
                centred_string(f"Completed {platform}", total_length=log_line_length)
            )
            self.logger.info(f"{log_line_sep * log_line_length}")

        self.logger.info(f"{log_line_sep * log_line_length}")
        self.logger.info(
            centred_string("ROMSearch complete", total_length=log_line_length)
        )
        self.logger.info(
            centred_string(
                f"Took {time.time()-start:.1f}s", total_length=log_line_length
            )
        )
        self.logger.info(f"{log_line_sep * log_line_length}")

        return True
