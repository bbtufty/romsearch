import copy
import os
import requests

import romsearch
from ..util import (centred_string,
                    load_yml,
                    setup_logger,
                    save_json,
                    )

RA_URL = "https://retroachievements.org/API"

class RAHasher:

    def __init__(self,
                 platform,
                 config_file=None,
                 config=None,
                 platform_config=None,
                 logger=None,
                 log_line_sep="=",
                 log_line_length=100,
                 ):
        """Get supported ROM hashes for RetroAchievements

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
            platform_config_file = os.path.join(mod_dir, "configs", "platforms", f"{platform}.yml")
            platform_config = load_yml(platform_config_file)
        self.platform_config = platform_config

        if logger is None:
            log_dir = self.config.get("dirs", {}).get("log_dir", os.path.join(os.getcwd(), "logs"))
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(log_level=log_level,
                                  script_name=f"RAHasher",
                                  log_dir=log_dir,
                                  )
        self.logger = logger

        self.ra_hash_dir = self.config.get("dirs", {}).get("ra_hash_dir", None)

        self.username = self.config.get("rahasher", {}).get("username", None)
        self.api_key = self.config.get("rahasher", {}).get("api_key", None)

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(self):
        """Run the RA hasher"""

        run_rahasher = True
        ra_hashes = None

        if self.ra_hash_dir is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(centred_string("No parsed_dat_dir defined in config file",
                                               total_length=self.log_line_length)
                                )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_rahasher = False
        if "ra_id" not in self.platform_config:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(centred_string("RA ID not defined in platform config file",
                                               total_length=self.log_line_length)
                                )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_rahasher = False
        if "ra_hash_method" not in self.platform_config:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(centred_string("RA hash method not defined in platform config file",
                                               total_length=self.log_line_length)
                                )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_rahasher = False
        if self.username is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(centred_string("RA username needs to be defined in config file",
                                               total_length=self.log_line_length)
                                )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_rahasher = False
        if self.api_key is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(centred_string("RA API key needs to be defined in config file",
                                               total_length=self.log_line_length)
                                )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_rahasher = False

        if run_rahasher:
            ra_hashes = self.run_rahasher()

        return ra_hashes

    def run_rahasher(self):
        """The main meat of running the RA hasher"""

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")
        self.logger.info(centred_string(f"Running RAHasher for {self.platform}",
                                        total_length=self.log_line_length)
                         )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        ra_hashes = self.get_ra_hashes()
        self.save_ra_hashes(ra_hashes)

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        return ra_hashes

    def get_ra_hashes(self):
        """Download the RA hashes using the API. Parse to JSON"""

        console_id = self.platform_config["ra_id"]

        url = f"{RA_URL}/API_GetGameList.php?z={self.username}&y={self.api_key}&i={console_id}&h=1&f=1"
        resp = requests.get(url=url)
        data = resp.json()

        hash_dict = {}
        for d in data:

            # RA uses "Title: Subtitle" logic, while No-Intro/Redump do not
            clean_title = d['Title'].replace(":", " -")

            hash_dict[clean_title] = copy.deepcopy(d)

        return hash_dict

    def save_ra_hashes(self, ra_hashes):
        """Save out the RA hashes to a file"""

        if not os.path.exists(self.ra_hash_dir):
            os.makedirs(self.ra_hash_dir)

        out_name = os.path.join(self.ra_hash_dir, f"{self.platform}.json")

        self.logger.info(centred_string(f"Saving to {out_name}",
                                        total_length=self.log_line_length)
                         )

        save_json(ra_hashes, out_name)

        return True
