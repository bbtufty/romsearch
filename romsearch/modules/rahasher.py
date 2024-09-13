import copy
import os
import requests
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


def format_game_list(
    in_file,
):
    """Format the GameList neatly

    Args:
        in_file (str): Input GameList file
    """

    data = load_json(in_file)

    ra_game_info = {}
    for d in data:
        # RA uses "Title: Subtitle" logic, while No-Intro/Redump do not
        clean_title = d["Title"].replace(":", " -")

        ra_game_info[clean_title] = copy.deepcopy(d)

    return ra_game_info


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

        cache_period = self.config.get("rahasher", {}).get("cache_period", 30)
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
        if "ra_hash_method" not in self.platform_config:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    "RA hash method not defined in platform config file",
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
        self.save_ra_game_info(ra_game_info)

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

        if diff.days > self.cache_period:
            self.logger.info(
                centred_string(
                    f"Downloading latest GameList to {game_list_file}",
                    total_length=self.log_line_length,
                )
            )
            self.download_ra_game_list(out_file=game_list_file)

        ra_game_info = format_game_list(game_list_file)

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

    def save_ra_game_info(
        self,
        ra_game_info,
    ):
        """Save out the RA game info to a file"""

        if not os.path.exists(self.ra_hash_dir):
            os.makedirs(self.ra_hash_dir)

        out_name = os.path.join(
            self.ra_hash_dir,
            f"{self.platform}.json",
        )

        self.logger.info(
            centred_string(
                f"Saving full game info to {out_name}",
                total_length=self.log_line_length,
            )
        )

        save_json(
            ra_game_info,
            out_name,
        )

        return True
