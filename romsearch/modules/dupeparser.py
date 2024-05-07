import os

import numpy as np
import requests

import romsearch
from ..util import (setup_logger,
                    create_bar,
                    load_yml,
                    get_parent_name,
                    get_short_name,
                    load_json,
                    save_json,
                    )

ID_CLONE_KEYS = [
    "cloneof",
    "cloneofid",
]


class DupeParser:

    def __init__(self,
                 config_file,
                 platform,
                 ):
        """Tool for figuring out a list of dupes

        TODO:
            - At some point, we might want to consider adding in the retool supersets
        """

        logger_add_dir = str(os.path.join(platform))

        self.logger = setup_logger(log_level="info",
                                   script_name=f"DupeParser",
                                   additional_dir=logger_add_dir,
                                   )

        config = load_yml(config_file)

        self.use_dat = config.get("dupeparser", {}).get("use_dat", True)
        self.use_retool = config.get("dupeparser", {}).get('use_retool', True)

        self.parsed_dat_dir = config.get("parsed_dat_dir", None)
        if self.use_dat and self.parsed_dat_dir is None:
            raise ValueError("Must specify parsed_dat_dir if using dat files")

        self.dupe_dir = config.get("dupe_dir", None)
        if self.dupe_dir is None:
            raise ValueError("dupe_dir should be specified in config file")

        self.platform = platform

        # Pull in platform config that we need
        mod_dir = os.path.dirname(romsearch.__file__)
        retool_config_file = os.path.join(mod_dir, "configs", "clonelists", f"retool.yml")
        retool_config = load_yml(retool_config_file)

        self.retool_url = retool_config.get("url", None)
        self.retool_platform_file = retool_config.get(platform, None)

        default_file = os.path.join(mod_dir, "configs", "defaults.yml")
        self.default_config = load_yml(default_file)

        regex_file = os.path.join(mod_dir, "configs", "regex.yml")
        self.regex_config = load_yml(regex_file)

    def run(self):
        """Run the dupe parser"""

        if (self.retool_platform_file is None or self.retool_url is None) and self.use_retool:
            self.logger.warning("retool config for the platform needs to be present if using retool")
            return False

        self.logger.info(create_bar(f"START DupeParser"))

        dupe_dict = self.get_dupe_dict()

        # Save out the dupe dict
        out_file = os.path.join(self.dupe_dir, f"{self.platform} (dupes).json")
        save_json(dupe_dict, out_file)

        self.logger.info(create_bar(f"FINISH DupeParser"))

        return True

    def get_dupe_dict(self):
        """Loop through potentially both the dat files and the retool config file to get out dupes"""

        dupe_dict = {}

        # Prefer retool dupes first
        if self.use_retool:
            self.logger.info("Gettings dupes from retool file")
            dupe_dict = self.get_retool_dupes(dupe_dict)
        if self.use_dat:
            self.logger.info("Gettings dupes from dat file")
            dupe_dict = self.get_dat_dupes(dupe_dict)

        dupe_dict = dict(sorted(dupe_dict.items()))

        return dupe_dict

    def get_dat_dupes(self, dupe_dict=None):
        """Get dupes from the dat that we've already parsed to JSON"""

        if dupe_dict is None:
            dupe_dict = {}

        json_dat = os.path.join(self.parsed_dat_dir, f"{self.platform} (dat parsed).json")
        if not os.path.exists(json_dat):
            self.logger.warning(f"No dat file found for {self.platform}")
            return None

        self.logger.info(f"Using parsed dat file {json_dat}")

        dat_dict = load_json(json_dat)

        all_keys = list(dat_dict.keys())

        for clone_name in dat_dict:
            for id_clone_key in ID_CLONE_KEYS:
                if id_clone_key in dat_dict[clone_name]:
                    clone_key = dat_dict[clone_name][id_clone_key]

                    # If it's an ID, find that ID
                    if id_clone_key == "cloneofid":

                        # Sometimes, IDs are missing from the dat so just move on
                        try:
                            dat_idx = np.where([dat_dict[key]["id"] == clone_key for key in dat_dict])[0][0]
                        except IndexError:
                            continue
                        parent_entry = dat_dict[all_keys[dat_idx]]
                        parent_name = parent_entry["name"]

                    elif id_clone_key == "cloneof":
                        # TODO
                        raise NotImplemented("Only current implemented for cloneofid")
                    else:
                        raise ValueError(f"Only know how to parse {ID_CLONE_KEYS}")

                    # Get short names here
                    # parent_game_name = get_game_name(parent_name)
                    parent_game_name = get_short_name(parent_name,
                                                      default_config=self.default_config,
                                                      regex_config=self.regex_config,
                                                      )
                    clone_short_name = get_short_name(clone_name,
                                                      default_config=self.default_config,
                                                      regex_config=self.regex_config,
                                                      )

                    # If the names are the same, just skip
                    if parent_game_name == clone_short_name:
                        continue

                    found_parent_name = get_parent_name(game_name=parent_game_name,
                                                        dupe_dict=dupe_dict,
                                                        )
                    if found_parent_name not in dupe_dict:
                        dupe_dict[found_parent_name] = {}

                    dupe_dict[found_parent_name][clone_short_name] = {"priority": 1}

        return dupe_dict

    def get_retool_dupes(self, dupe_dict=None):
        """Get dupes from the retool curated list"""

        if dupe_dict is None:
            dupe_dict = {}

        retool_dupes = self.get_retool_dupe_dict()
        for retool_dupe in retool_dupes:

            # If we don't have titles within the dupe dict, skip
            if "titles" not in retool_dupe:
                continue

            group = retool_dupe["group"]
            group_titles = [get_short_name(f["searchTerm"],
                                           default_config=self.default_config,
                                           regex_config=self.regex_config,
                                           )
                            for f in retool_dupe["titles"]]
            priorities = [f.get("priority", 1) for f in retool_dupe["titles"]]

            # Parse down to the game name here
            # if "(" in group:
            #     group_parsed = get_game_name(group)
            # else:
            #     group_parsed = copy.deepcopy(group)
            group_parsed = get_short_name(group,
                                          default_config=self.default_config,
                                          regex_config=self.regex_config,
                                          )

            found_parent_name = get_parent_name(game_name=group_parsed,
                                                dupe_dict=dupe_dict,
                                                )
            if found_parent_name not in dupe_dict:
                dupe_dict[found_parent_name] = {}

            for i, g in enumerate(group_titles):
                dupe_dict[found_parent_name][g] = {"priority": priorities[i]}

        return dupe_dict

    def download_retool_dupe(self,
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
            raise ValueError("Should specify an out_file to save the retool dupe list to")

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(retool_full_file)

        return True

    def get_retool_dupe_dict(self):
        """Pull the retool duplicates out of the clonelist file"""

        if not os.path.exists(self.dupe_dir):
            os.makedirs(self.dupe_dir)

        retool_dupe_file = os.path.join(self.parsed_dat_dir, f"{self.platform} (retool).json")
        if not os.path.exists(retool_dupe_file):

            if not os.path.exists(self.parsed_dat_dir):
                os.makedirs(self.parsed_dat_dir)

            self.logger.info("No retool dupe file found. Downloading")
            self.download_retool_dupe(retool_dupe_file)

        retool_dupes = load_json(retool_dupe_file)

        # Check if there's a more updated file, if so download it
        local_file_time = retool_dupes["description"]["lastUpdated"]
        remote_file_time = self.download_retool_dupe(just_date=True)

        if not local_file_time == remote_file_time:
            self.logger.info("More up-to-date dupe file found. Will download")
            self.download_retool_dupe(retool_dupe_file)

        self.logger.info(f"Using retool clonelist {retool_dupe_file}")

        retool_dupes = load_json(retool_dupe_file)
        retool_dupes = retool_dupes["variants"]

        return retool_dupes
