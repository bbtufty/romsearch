import copy
import os
import re

import romsearch
from ..util import (centred_string,
                    left_aligned_string,
                    setup_logger,
                    get_file_time,
                    load_yml,
                    load_json,
                    get_game_name,
                    )

DICT_DEFAULT_VALS = {
    "bool": False,
    "str": "",
    "list": []
}


def find_pattern(regex, search_str, group_number=0):
    """
    Take a regex pattern and find potential matches within a search string
    """
    regex_search_str = None

    regex_search = re.search(regex, search_str)
    if regex_search:
        regex_search_str = regex_search.group(group_number)

    return regex_search_str


def get_pattern_val(regex,
                    tag,
                    regex_type,
                    pattern_mappings=None
                    ):
    """Get values out from a regex pattern, optionally mapping back to something more readable for lists"""

    pattern_string = find_pattern(regex, tag)

    if pattern_string is not None:
        pattern_string = pattern_string.strip("()")

        if regex_type == "bool":
            pattern_val = True
        elif regex_type == "str":
            pattern_val = pattern_string
        elif regex_type == "list":

            if pattern_mappings is not None:
                parsed_pattern_string = []
                # Match to pattern mappings
                for p in pattern_mappings:
                    if re.search(pattern_mappings[p], pattern_string):
                        parsed_pattern_string.append(p)
            else:
                # Split, and remove and trailing whitespace
                parsed_pattern_string = pattern_string.split(",")
                parsed_pattern_string = [s.strip() for s in parsed_pattern_string]
            pattern_val = parsed_pattern_string
        else:
            raise ValueError("regex_type should be one of 'bool', 'str', or 'list'")

    else:
        pattern_val = None

    return pattern_val


class ROMParser:

    def __init__(self,
                 platform,
                 game,
                 config_file=None,
                 config=None,
                 platform_config=None,
                 default_config=None,
                 regex_config=None,
                 logger=None,
                 log_line_sep="=",
                 log_line_length=100,
                 ):
        """ROM parser tool

        This works per-game, per-platform, so must be specified here

        Args:
            platform (str): Platform name
            game (str): Game name
            config_file (str, optional): path to config file. Defaults to None.
            config (dict, optional): configuration dictionary. Defaults to None.
            platform_config (dict, optional): platform configuration dictionary. Defaults to None.
            default_config (dict, optional): default configuration dictionary. Defaults to None.
            regex_config (dict, optional): regex configuration dictionary. Defaults to None.
            logger (logging.Logger, optional): logger instance. Defaults to None.
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

        self.game = game

        if logger is None:
            log_dir = self.config.get("dirs", {}).get("log_dir", os.path.join(os.getcwd(), "logs"))
            logger_add_dir = str(os.path.join(platform, game))
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(log_level=log_level,
                                  script_name=f"ROMParser",
                                  log_dir=log_dir,
                                  additional_dir=logger_add_dir,
                                  )
        self.logger = logger

        mod_dir = os.path.dirname(romsearch.__file__)

        if default_config is None:
            default_file = os.path.join(mod_dir, "configs", "defaults.yml")
            default_config = load_yml(default_file)
        self.default_config = default_config

        if regex_config is None:
            regex_file = os.path.join(mod_dir, "configs", "regex.yml")
            regex_config = load_yml(regex_file)
        self.regex_config = regex_config

        if platform_config is None:
            platform_config_file = os.path.join(mod_dir, "configs", "platforms", f"{platform}.yml")
            platform_config = load_yml(platform_config_file)
        self.platform_config = platform_config

        self.raw_dir = self.config.get("dirs", {}).get("raw_dir", None)
        if not self.raw_dir:
            raise ValueError("raw_dir must be specified in config.yml")

        self.use_dat = self.config.get("romparser", {}).get("use_dat", True)
        self.use_retool = self.config.get("romparser", {}).get("use_retool", True)
        self.use_filename = self.config.get("romparser", {}).get("use_filename", True)
        self.dry_run = self.config.get("romparser", {}).get("dry_run", False)

        # If we're using the dat file, pull it out here
        self.dat = None
        if self.use_dat:
            dat_dir = self.config.get("dirs", {}).get("parsed_dat_dir", None)
            if dat_dir is None:
                raise ValueError("parsed_dat_dir must be specified in config.yml")
            dat_file = os.path.join(dat_dir, f"{platform} (dat parsed).json")
            if os.path.exists(dat_file):
                self.dat = load_json(dat_file)

        # If we're using the retool file, pull it out here
        self.retool = None
        if self.use_retool:
            dat_dir = self.config.get("dirs", {}).get("parsed_dat_dir", None)
            if dat_dir is None:
                raise ValueError("parsed_dat_dir must be specified in config.yml")
            retool_file = os.path.join(dat_dir, f"{platform} (retool).json")
            if os.path.exists(retool_file):
                self.retool = load_json(retool_file)

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(self,
            files,
            ):
        """Run the ROM parser"""

        game_dict = {}

        self.logger.debug(f"{self.log_line_sep * self.log_line_length}")
        self.logger.debug(centred_string(f"Running ROMParser for {self.game}",
                                         total_length=self.log_line_length)
                         )
        self.logger.debug(f"{self.log_line_sep * self.log_line_length}")

        for f in files:
            game_dict[f] = self.parse_file(f)

            # Include the priority
            game_dict[f]["priority"] = files[f]["priority"]

        return game_dict

    def parse_file(self,
                   f,
                   ):
        """Parse useful info out of a specific file"""

        file_dict = {}

        if self.use_filename:
            file_dict = self.parse_filename(f, file_dict)
        if self.use_retool:
            file_dict = self.parse_retool(f, file_dict)
        if self.use_dat:
            file_dict = self.parse_dat(f, file_dict)

        # Any last minute finalisations
        self.finalise_file_dict(file_dict)

        # File modification time
        full_file_path = os.path.join(self.raw_dir, self.platform, f)
        file_time = get_file_time(full_file_path,
                                  datetime_format=self.default_config["datetime_format"],
                                  )
        file_dict["file_mod_time"] = file_time

        # Log out these tags in a nice readable way
        self.logger.debug(centred_string(f"{f}:",
                                         total_length=self.log_line_length)
                          )

        # Track the various tags we can have
        true_tags = []
        false_tags = []
        str_tags = {}
        list_tags = {}

        for key in file_dict:
            if isinstance(file_dict[key], bool):
                if file_dict[key]:
                    true_tags.append(key)
                else:
                    false_tags.append(key)
            elif isinstance(file_dict[key], str):
                str_tags[key] = file_dict[key]
            elif isinstance(file_dict[key], list):
                list_tags[key] = file_dict[key]
            else:
                raise ValueError(f"{file_dict[key]} is not something I know how to parse")

        # Log the string tags
        self.logger.debug(left_aligned_string(f"String tags:",
                                              total_length=self.log_line_length)
                          )
        for tag in str_tags:
            if str_tags[tag] == "":
                continue
            self.logger.debug(left_aligned_string(f"-> {tag}: {str_tags[tag]}",
                                                  total_length=self.log_line_length)
                              )

        # Log the list tags
        self.logger.debug(left_aligned_string(f"List tags:",
                                              total_length=self.log_line_length)
                          )
        for tag in list_tags:
            if not list_tags[tag]:
                continue
            self.logger.debug(left_aligned_string(f"-> {tag}: {', '.join(str(i) for i in list_tags[tag])}",
                                                  total_length=self.log_line_length)
                              )

        # Log the True bool tags
        self.logger.debug(left_aligned_string(f"Tagged:",
                                              total_length=self.log_line_length)
                          )
        for tag in true_tags:
            self.logger.debug(left_aligned_string(f"-> {tag}",
                                                  total_length=self.log_line_length)
                              )

        # Log the False bool tags
        self.logger.debug(left_aligned_string(f"Not tagged:",
                                              total_length=self.log_line_length)
                          )
        for tag in false_tags:
            self.logger.debug(left_aligned_string(f"-> {tag}",
                                                  total_length=self.log_line_length)
                              )

        self.logger.debug(f"{'-' * self.log_line_length}")

        return file_dict

    def parse_retool(self, f, file_dict=None):
        """Parse info out of the retool file"""

        if file_dict is None:
            file_dict = {}

        if self.retool is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(centred_string(f"No retool file found for {self.platform}. Skipping",
                                             total_length=self.log_line_length)
                              )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            return file_dict

        # Pull out the game name
        game_name = get_game_name(f)

        # Loop over the variants, see if we get a match
        found_cat = False
        for retool_dict in self.retool["variants"]:

            if found_cat:
                continue

            # If we don't have titles within the dupe dict, skip
            if "titles" not in retool_dict:
                continue

            retool_variants = [f["searchTerm"].lower() for f in retool_dict["titles"]]

            if game_name.lower() in retool_variants:

                found_cat = True

                # If we have categories, set these to True
                retool_cats = retool_dict.get("categories", [])
                for retool_cat in retool_cats:
                    file_cat = retool_cat.lower().replace(" ", "_")
                    file_dict[file_cat] = True

        return file_dict

    def parse_dat(self, f, file_dict=None):
        """Parse info out of the dat file"""

        if file_dict is None:
            file_dict = {}

        if self.dat is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(centred_string(f"No dat file found for {self.platform}. Skipping",
                                             total_length=self.log_line_length)
                              )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            return file_dict

        # Remember there aren't zips in the dat entries
        dat_entry = self.dat.get(f.strip(".zip"), None)
        if not dat_entry:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(centred_string(f"No dat entry found for {f}. Skipping",
                                             total_length=self.log_line_length)
                              )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            return file_dict

        dat_categories = self.default_config.get("dat_categories", [])
        for dat_cat in dat_categories:

            dat_val = dat_entry.get("category", "")
            cat_val = dat_val == dat_cat

            dat_cat_dict = dat_cat.lower().replace(" ", "_")
            if dat_cat_dict in file_dict:
                file_dict[dat_cat_dict] = file_dict[dat_cat_dict] | cat_val
            else:
                file_dict[dat_cat_dict] = cat_val

        return file_dict

    def finalise_file_dict(self,
                           file_dict,
                           ):
        """Do any last minute finalisation to the file dict"""

        file_dict = self.set_game_category(file_dict)
        file_dict = self.set_implicit_languages(file_dict)

        return file_dict

    def set_game_category(self,
                          file_dict,
                          ):
        """If a dat category hasn't been set, set it to game"""

        dat_categories = self.default_config.get("dat_categories", [])

        for d in dat_categories:
            d_sanitized = d.lower().replace(" ", "_")

            if d_sanitized not in file_dict:
                file_dict[d_sanitized] = False

        if all([file_dict[d.lower().replace(" ", "_")] is False for d in dat_categories]):
            file_dict["games"] = True

        return file_dict

    def set_implicit_languages(self,
                               file_dict,
                               ):
        """Set implicit language from region, if we don't already have languages"""

        implied_languages = self.default_config.get("implied_languages", {})

        # Only set if languages is an empty list
        if not file_dict["languages"]:
            for r in file_dict["regions"]:
                if r in implied_languages:
                    file_dict["languages"].append(implied_languages[r])

        return file_dict

    def parse_filename(self, f, file_dict=None):
        """Parse info out of filename"""

        if file_dict is None:
            file_dict = {}

        # Split file into tags
        tags = [f'({x}' for x in f.strip(".zip").split(' (')][1:]

        for regex_key in self.regex_config:

            regex_type = self.regex_config[regex_key].get("type", "bool")
            search_tags = self.regex_config[regex_key].get("search_tags", True)
            group = self.regex_config[regex_key].get("group", None)
            regex_flags = self.regex_config[regex_key].get("flags", "I")
            transform_pattern = self.regex_config[regex_key].get("transform_pattern", None)
            transform_repl = self.regex_config[regex_key].get("transform_repl", None)

            dict_default_val = DICT_DEFAULT_VALS.get(regex_type, None)
            if dict_default_val is None:
                raise ValueError(f"regex_type should be one of {list(DICT_DEFAULT_VALS.keys())}")

            if regex_key not in file_dict:
                file_dict[regex_key] = dict_default_val

            if regex_flags == "NOFLAG":
                regex_flags = re.NOFLAG
            elif regex_flags == "I":
                regex_flags = re.I
            else:
                raise ValueError("regex_flags should be one of 'NOFLAG', 'I'")

            pattern = self.regex_config[regex_key]["pattern"]

            pattern_mappings = None

            if regex_type == "list":

                if isinstance(self.default_config[regex_key], dict):
                    str_to_join = [self.default_config[regex_key][key] for key in self.default_config[regex_key]]
                    pattern_mappings = self.default_config[regex_key]
                else:
                    str_to_join = copy.deepcopy(self.default_config[regex_key])

                pattern = pattern.replace(f"[{regex_key}]", "|".join(str_to_join))

            regex = re.compile(pattern, flags=regex_flags)
            if search_tags:

                found_tag = False

                for tag in tags:

                    if found_tag:
                        continue

                    pattern_string = get_pattern_val(regex,
                                                     tag,
                                                     regex_type,
                                                     pattern_mappings=pattern_mappings,
                                                     )
                    if pattern_string is not None:

                        if transform_pattern is not None:

                            pattern_string = re.sub(transform_pattern, transform_repl, pattern_string)

                        file_dict[regex_key] = pattern_string
                        found_tag = True
            else:
                pattern_string = get_pattern_val(regex,
                                                 f,
                                                 regex_type,
                                                 pattern_mappings=pattern_mappings
                                                 )
                if pattern_string is not None:
                    file_dict[regex_key] = pattern_string

            # Update groups, if needed
            if group is not None:
                if group not in file_dict:
                    file_dict[group] = dict_default_val

                if regex_type == "bool":
                    file_dict[group] = file_dict[group] | file_dict[regex_key]
                elif regex_type == "str":
                    if file_dict[group] and file_dict[regex_key]:
                        raise ValueError("Can't combine multiple groups with type str")
                    else:
                        file_dict[group] += file_dict[regex_key]
                elif regex_type == "list":
                    file_dict[group].extend(file_dict[regex_key])
                else:
                    raise ValueError(f"regex_type should be one of {list(DICT_DEFAULT_VALS.keys())}")

        return file_dict
