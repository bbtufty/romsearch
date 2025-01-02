import copy
import os
import requests

import romsearch
from ..util import (
    centred_string,
    setup_logger,
    load_yml,
    load_json,
    save_json,
)

ID_CLONE_KEYS = [
    "cloneof",
    "cloneofid",
]


class DupeParser:

    def __init__(
        self,
        platform=None,
        config_file=None,
        config=None,
        default_config=None,
        regex_config=None,
        logger=None,
        log_line_sep="=",
        log_line_length=100,
    ):
        """Tool for figuring out a list of dupes

        Args:
            platform (str, optional): Platform name. Defaults to None, which will throw a ValueError.
            config_file (str, optional): Path to config file. Defaults to None
            config (dict, optional): Configuration dictionary. Defaults to None
            default_config (dict, optional): Default configuration dictionary. Defaults to None
            regex_config (dict, optional): Configuration dictionary for regex search. Defaults to None
            logger (logging.Logger, optional): Logger instance. Defaults to None
            log_line_length (int, optional): Line length of log. Defaults to 100

        TODO:
            - At some point, we might want to consider adding in the retool supersets
        """

        if platform is None:
            raise ValueError("platform must be specified")
        self.platform = platform

        if config_file is None and config is None:
            raise ValueError("config_file or config must be specified")

        if config is None:
            config = load_yml(config_file)
        self.config = config

        if logger is None:
            log_dir = self.config.get("dirs", {}).get(
                "log_dir", os.path.join(os.getcwd(), "logs")
            )
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(
                log_level=log_level,
                script_name=f"DupeParser",
                log_dir=log_dir,
                additional_dir=platform,
            )
        self.logger = logger

        # self.use_dat = self.config.get("dupeparser", {}).get("use_dat", True)
        self.use_retool = self.config.get("dupeparser", {}).get("use_retool", True)

        self.parsed_dat_dir = self.config.get("dirs", {}).get("parsed_dat_dir", None)
        if self.use_retool and self.parsed_dat_dir is None:
            raise ValueError("Must specify parsed_dat_dir if using retool files")

        self.dupe_dir = self.config.get("dirs", {}).get("dupe_dir", None)
        if self.dupe_dir is None:
            raise ValueError("dupe_dir should be specified in config file")

        # Pull in platform config that we need
        mod_dir = os.path.dirname(romsearch.__file__)
        retool_config_file = os.path.join(
            mod_dir, "configs", "clonelists", f"retool.yml"
        )
        retool_config = load_yml(retool_config_file)

        self.retool_url = retool_config.get("url", None)
        self.retool_platform_file = retool_config.get(platform, None)

        if default_config is None:
            default_file = os.path.join(mod_dir, "configs", "defaults.yml")
            default_config = load_yml(default_file)
        self.default_config = default_config

        if regex_config is None:
            regex_file = os.path.join(mod_dir, "configs", "regex.yml")
            regex_config = load_yml(regex_file)
        self.regex_config = regex_config

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(self):
        """Run the dupe parser"""

        if (
            self.retool_platform_file is None or self.retool_url is None
        ) and self.use_retool:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    "retool config for the platform needs to be present "
                    "if using retool",
                    total_length=self.log_line_length,
                )
            )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            return False

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")
        self.logger.info(
            centred_string("Running DupeParser", total_length=self.log_line_length)
        )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        dupe_dict, retool_dict = self.get_dupe_dict()

        # Save out the dupe dict
        out_file = os.path.join(self.dupe_dir, f"{self.platform} (dupes).json")
        save_json(dupe_dict, out_file)

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        return dupe_dict, retool_dict

    def get_dupe_dict(self):
        """Loop through potentially the retool file to get out dupes"""

        dupe_dict = {}

        # Retool dupes
        retool_dict = None
        if self.use_retool:
            dupe_dict, retool_dict = self.get_retool_dupes(dupe_dict)

        dupe_dict = dict(sorted(dupe_dict.items()))

        return dupe_dict, retool_dict

    def get_retool_dupes(self, dupe_dict=None):
        """Get dupes from the retool curated list"""

        if dupe_dict is None:
            dupe_dict = {}

        retool_dupes = self.get_retool_dupe_dict()
        for retool_dupe in retool_dupes:

            # If we don't have titles or compilations within the dupe dict, skip
            if "titles" not in retool_dupe and "compilations" not in retool_dupe:
                continue

            # Get group name
            group = retool_dupe["group"]

            # Ensure we've not mismatched upper/lowercase
            group_lower = group.lower()
            dupe_dict_keys = [key for key in dupe_dict.keys()]
            dupe_dict_keys_lower = [key.lower() for key in dupe_dict.keys()]

            if group_lower not in dupe_dict_keys_lower:
                final_group = copy.deepcopy(group)
            else:
                final_group_idx = dupe_dict_keys_lower.index(group_lower)
                final_group = dupe_dict_keys[final_group_idx]

            # Pull out individual titles
            if "titles" in retool_dupe:

                if final_group not in dupe_dict:
                    dupe_dict[final_group] = {}

                for title in retool_dupe["titles"]:
                    title_g = title["searchTerm"]
                    name_type = title.get("nameType", None)
                    priority = title.get("priority", 1)
                    filters = title.get("filters", None)

                    dupe_dict[group][title_g] = {
                        "name_type": name_type,
                        "priority": priority,
                        "filters": filters,
                    }

            # Check for compilations. If we have them, pull them out and potentially the title position
            if "compilations" in retool_dupe:

                if final_group not in dupe_dict:
                    dupe_dict[final_group] = {}

                for compilation in retool_dupe["compilations"]:
                    comp_g = compilation["searchTerm"]
                    name_type = compilation.get("nameType", None)
                    title_pos = compilation.get("titlePosition", None)
                    priority = compilation.get("priority", 1)
                    filters = compilation.get("filters", None)

                    dupe_dict[group][comp_g] = {
                        "name_type": name_type,
                        "is_compilation": True,
                        "priority": priority,
                        "title_pos": title_pos,
                        "filters": filters,
                    }

            # Check for supersets. If we have them, pull them out and potentially the title position
            if "supersets" in retool_dupe:

                if final_group not in dupe_dict:
                    dupe_dict[final_group] = {}

                for superset in retool_dupe["supersets"]:
                    sup_g = superset["searchTerm"]
                    name_type = superset.get("nameType", None)
                    title_pos = superset.get("titlePosition", None)
                    priority = superset.get("priority", 1)
                    english_friendly = superset.get("englishFriendly", False)
                    filters = superset.get("filters", None)

                    dupe_dict[group][sup_g] = {
                        "name_type": name_type,
                        "is_superset": True,
                        "priority": priority,
                        "english_friendly": english_friendly,
                        "title_pos": title_pos,
                        "filters": filters,
                    }

        return dupe_dict, retool_dupes

    def download_retool_dupe(
        self,
        out_file=None,
        just_date=False,
    ):
        """Download the retool curated list, optionally just returning the last modified date"""

        retool_url = f"{self.retool_url}/{self.retool_platform_file}"
        with requests.get(retool_url) as r:
            retool_dict = r.json()
            if just_date:
                return retool_dict["description"]["lastUpdated"]
            retool_full_file = r.text

        if out_file is None:
            raise ValueError(
                "Should specify an out_file to save the retool dupe list to"
            )

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(retool_full_file)

        return True

    def get_retool_dupe_dict(self):
        """Pull the retool duplicates out of the clonelist file"""

        if not os.path.exists(self.dupe_dir):
            os.makedirs(self.dupe_dir)

        retool_dupe_file = os.path.join(
            self.parsed_dat_dir, f"{self.platform} (retool).json"
        )
        if not os.path.exists(retool_dupe_file):

            if not os.path.exists(self.parsed_dat_dir):
                os.makedirs(self.parsed_dat_dir)

            self.logger.info(
                centred_string(
                    "No retool dupe file found. Downloading",
                    total_length=self.log_line_length,
                )
            )
            self.download_retool_dupe(retool_dupe_file)

        retool_dupes = load_json(retool_dupe_file)

        # Check if there's a more updated file, if so download it
        local_file_time = retool_dupes["description"]["lastUpdated"]
        remote_file_time = self.download_retool_dupe(just_date=True)

        if not local_file_time == remote_file_time:
            self.logger.info(
                centred_string(
                    "More up-to-date dupe file found. Will download",
                    total_length=self.log_line_length,
                )
            )
            self.download_retool_dupe(retool_dupe_file)

        self.logger.info(
            centred_string(
                f"Using retool clonelist {retool_dupe_file}",
                total_length=self.log_line_length,
            )
        )

        retool_dupes = load_json(retool_dupe_file)
        retool_dupes = retool_dupes["variants"]

        return retool_dupes
