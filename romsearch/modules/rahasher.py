import copy
import os
import requests
import time
from datetime import datetime

import romsearch
from ..util import (
    centred_string,
    load_yml,
    setup_logger,
    load_json,
    save_json,
    get_file_time,
)

RA_URL = "https://retroachievements.org/API"


class RAHasher:

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
        """Get supported ROM files and hashes for RetroAchievements

        This works per-platform, so must be specified here

        Args:
            platform (str): Platform name
            config_file (str, optional): Path to config file. Defaults to None.
            config (dict, optional): Configuration dictionary. Defaults to None.
            platform_config (dict, optional): Platform configuration dictionary. Defaults to None
            logger (logging.Logger, optional): Logger instance. Defaults to None.
            log_line_length (int, optional): Line length of log. Defaults to 100
        """

        if platform is None:
            raise ValueError("platform must be specified")
        self.platform = platform

        if config_file is None and config is None:
            raise ValueError("config_file or config must be specified")

        if config is None:
            config = load_yml(config_file)
        self.config = config

        # Read in the specific platform configuration
        mod_dir = os.path.dirname(romsearch.__file__)

        if platform_config is None:
            platform_config_file = os.path.join(
                mod_dir, "configs", "platforms", f"{platform}.yml"
            )
            platform_config = load_yml(platform_config_file)
        self.platform_config = platform_config

        if logger is None:
            log_dir = self.config.get("dirs", {}).get(
                "log_dir", os.path.join(os.getcwd(), "logs")
            )
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(
                log_level=log_level,
                script_name=f"RAHasher",
                log_dir=log_dir,
            )
        self.logger = logger

        self.ra_hash_dir = self.config.get("dirs", {}).get("ra_hash_dir", None)

        self.username = self.config.get("rahasher", {}).get("username", None)
        self.api_key = self.config.get("rahasher", {}).get("api_key", None)

        cache_period = self.config.get("rahasher", {}).get("cache_period", 1)
        if isinstance(cache_period, str):
            cache_period = float(cache_period)
        self.cache_period = cache_period

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(self):
        """Run the RA hasher"""

        run_rahasher = True
        ra_game_info = None

        if self.ra_hash_dir is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    "No parsed_dat_dir defined in config file",
                    total_length=self.log_line_length,
                )
            )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_rahasher = False
        if "ra_id" not in self.platform_config:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    "RA ID not defined in platform config file",
                    total_length=self.log_line_length,
                )
            )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_rahasher = False
        if self.username is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    "RA username needs to be defined in config file",
                    total_length=self.log_line_length,
                )
            )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_rahasher = False
        if self.api_key is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    "RA API key needs to be defined in config file",
                    total_length=self.log_line_length,
                )
            )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_rahasher = False

        if run_rahasher:

            if not os.path.exists(self.ra_hash_dir):
                os.makedirs(self.ra_hash_dir)

            ra_game_info = self.run_rahasher()

        return ra_game_info

    def run_rahasher(self):
        """The main meat of running the RA hasher"""

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")
        self.logger.info(
            centred_string(
                f"Running RAHasher for {self.platform}",
                total_length=self.log_line_length,
            )
        )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        ra_game_info = self.get_ra_game_info()

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        return ra_game_info

    def get_ra_game_info(self):
        """Download or read in RA game info."""

        game_list_file = os.path.join(
            self.ra_hash_dir, f"{self.platform} GameList.json"
        )
        game_list_modtime = get_file_time(
            game_list_file,
            return_as_str=False,
        )

        cur_time = datetime.now()
        diff = cur_time - game_list_modtime

        # If we're still in the cache period, don't overwrite
        self.logger.info(
            centred_string(
                f"Last GameList cache {diff.days} days ago",
                total_length=self.log_line_length,
            )
        )
        if diff.days > self.cache_period:
            self.logger.info(
                centred_string(
                    f"Downloading latest GameList to {game_list_file}",
                    total_length=self.log_line_length,
                )
            )
            self.download_ra_game_list(out_file=game_list_file)

        # Now get existing game info, if it exists
        game_info_file = os.path.join(
            self.ra_hash_dir,
            f"{self.platform}.json",
        )

        if not os.path.exists(game_info_file):
            ra_game_info = {}
        else:
            ra_game_info = load_json(game_info_file)

        self.logger.info(
            centred_string(
                f"Pulling game info out to {game_info_file}",
                total_length=self.log_line_length,
            )
        )
        ra_game_info = self.format_game_list(game_list_file,
                                             ra_game_info=ra_game_info,
                                             )

        self.save_ra_game_info(
            ra_game_info,
            game_info_file,
        )

        return ra_game_info

    def download_ra_game_list(
        self,
        out_file,
    ):
        """Download the RA GameList using the API

        Args:
            out_file (string): output file name.
        """

        console_id = self.platform_config["ra_id"]

        url = f"{RA_URL}/API_GetGameList.php?z={self.username}&y={self.api_key}&i={console_id}&h=1&f=1"
        resp = requests.get(url=url)
        data = resp.json()

        save_json(data, out_file)

        return True

    def format_game_list(
        self,
        in_file,
        ra_game_info=None,
        sleep_time=0.5,
    ):
        """Format the GameList neatly

        Args:
            in_file (str): Input GameList file
            ra_game_info (dict): RA game info. Defaults to None, which will use an empty
                dictionary
            sleep_time (float): Sleep time for API queries. Defaults to 0.5
        """

        game_list = load_json(in_file)

        if ra_game_info is None:
            ra_game_info = {}

        self.logger.info(
            centred_string(
                f"Found {len(game_list)} RetroAchievements entries with achievements",
                total_length=self.log_line_length,
            )
        )

        n_updated = 0
        for d in game_list:

            # RA uses "Title: Subtitle" logic, while No-Intro/Redump do not
            clean_title = d["Title"].replace(":", " -")

            # Get out modification times, if they exist
            game_list_mod_time = d["DateModified"]
            ra_game_info_mod_time = ra_game_info.get(clean_title, {}).get("DateModified", None)

            # If they match, skip
            if game_list_mod_time == ra_game_info_mod_time:
                continue

            # Format this string neatly
            self.logger.info(
                centred_string(
                    f"Getting/updating hashes for {clean_title}",
                    total_length=self.log_line_length,
                )
            )

            # Use ID to get all the useful hash info
            game_hashes = self.get_game_hash(d["ID"])
            d["Hashes"] = copy.deepcopy(game_hashes)

            ra_game_info[clean_title] = copy.deepcopy(d)

            # To avoid overloading the API, add a pause here
            time.sleep(sleep_time)

            n_updated += 1

        self.logger.info(
            centred_string(
                f"Added/updated {n_updated} game entries",
                total_length=self.log_line_length,
            )
        )

        # Sort these hashes
        ra_game_info = dict(sorted(ra_game_info.items()))

        # Remove things in the RA game info that aren't in the game list
        all_game_list_titles = [f["Title"] for f in game_list]
        all_ra_game_info_fixed_title = list(ra_game_info.keys())
        all_ra_game_info_title = [ra_game_info[f]["Title"] for f in all_ra_game_info_fixed_title]

        not_present_list = list(set(all_ra_game_info_title) - set(all_game_list_titles))
        for np in not_present_list:
            idx_np = all_ra_game_info_title.index(np)
            np_mapped = all_ra_game_info_fixed_title[idx_np]
            ra_game_info.pop(np_mapped, None)

        return ra_game_info

    def get_game_hash(
        self,
        game_id,
    ):
        """Using a game ID, get list of the game hashes"""

        url = f"{RA_URL}/API_GetGameHashes.php?i={game_id}&y={self.api_key}&z={self.username}"
        resp = requests.get(url=url)
        game_hashes = resp.json()

        game_hashes = game_hashes["Results"]

        return game_hashes

    def save_ra_game_info(
        self,
        ra_game_info,
        out_file,
    ):
        """Save out the RA game info to a file

        Args:
            ra_game_info (dict): RA game info
            out_file (string): output file name
        """

        if not os.path.exists(self.ra_hash_dir):
            os.makedirs(self.ra_hash_dir)

        self.logger.info(
            centred_string(
                f"Saving full game info to {out_file}",
                total_length=self.log_line_length,
            )
        )

        save_json(
            ra_game_info,
            out_file,
        )

        return True
