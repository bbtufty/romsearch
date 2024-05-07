import copy
import os
import re
import time
from datetime import datetime

import romsearch
from ..util import (setup_logger,
                    create_bar,
                    load_yml,
                    load_json,
                    get_bracketed_file_pattern,
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
                    if re.match(pattern_mappings[p], pattern_string):
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


def get_file_time(f,
                  datetime_format,
                  ):
    """Get created file time from the file itself"""

    if os.path.exists(f):
        ti_m = os.path.getmtime(f)
        date_ti_m = datetime.strptime(time.ctime(ti_m), "%a %b %d %H:%M:%S %Y")
    else:
        date_ti_m = datetime(year=1900, month=1, day=1, hour=0, minute=0, second=0)
    date_ti_m_str = date_ti_m.strftime(format=datetime_format)

    return date_ti_m_str


class ROMParser:

    def __init__(self,
                 config_file,
                 platform,
                 game,
                 ):
        """ROM parser tool

        This works per-game, per-platform, so must be specified here

        TODO:
            - Default implied languages from regions
        """

        if platform is None:
            raise ValueError("platform must be specified")
        self.platform = platform

        logger_add_dir = str(os.path.join(platform, game))

        self.logger = setup_logger(log_level="info",
                                   script_name=f"ROMParser",
                                   additional_dir=logger_add_dir,
                                   )

        config = load_yml(config_file)

        mod_dir = os.path.dirname(romsearch.__file__)

        default_config_file = os.path.join(mod_dir, "configs", "defaults.yml")
        self.default_config = load_yml(default_config_file)

        regex_file = os.path.join(mod_dir, "configs", "regex.yml")
        self.regex = load_yml(regex_file)

        platform_config_file = os.path.join(mod_dir, "configs", "platforms", f"{platform}.yml")
        self.platform_config = load_yml(platform_config_file)

        self.raw_dir = config.get("raw_dir", None)
        if not self.raw_dir:
            raise ValueError("raw_dir must be specified in config.yml")

        self.use_dat = config.get("romparser", {}).get("use_dat", True)
        self.use_retool = config.get("romparser", {}).get("use_retool", True)
        self.use_filename = config.get("romparser", {}).get("use_filename", True)
        self.dry_run = config.get("romparser", {}).get("dry_run", False)

        # If we're using the dat file, pull it out here
        self.dat = None
        if self.use_dat:
            dat_dir = config.get("parsed_dat_dir", None)
            if dat_dir is None:
                raise ValueError("parsed_dat_dir must be specified in config.yml")
            dat_file = os.path.join(dat_dir, f"{platform} (dat parsed).json")
            if os.path.exists(dat_file):
                self.dat = load_json(dat_file)

        # If we're using the retool file, pull it out here
        self.retool = None
        if self.use_retool:
            dat_dir = config.get("parsed_dat_dir", None)
            if dat_dir is None:
                raise ValueError("parsed_dat_dir must be specified in config.yml")
            retool_file = os.path.join(dat_dir, f"{platform} (retool).json")
            if os.path.exists(retool_file):
                self.retool = load_json(retool_file)

    def run(self,
            files,
            ):
        """Run the ROM parser"""

        self.logger.info(create_bar(f"START ROMParser"))

        game_dict = {}

        for f in files:
            game_dict[f] = self.parse_file(f)

            # Include the priority
            game_dict[f]["priority"] = files[f]["priority"]

        self.logger.info(create_bar(f"FINISH ROMParser"))

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

        self.logger.info(f"{f}: {file_dict}")

        return file_dict

    def parse_retool(self, f, file_dict=None):
        """Parse info out of the retool file"""

        if file_dict is None:
            file_dict = {}

        if self.retool is None:
            self.logger.warning(f"No retool file found for {self.platform}. Skipping")
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
            self.logger.warning(f"No dat file found for {self.platform}. Skipping")
            return file_dict

        # Remember there aren't zips in the dat entries
        dat_entry = self.dat.get(f.strip(".zip"), None)
        if not dat_entry:
            self.logger.warning(f"No dat entry found for {f}. Skipping")
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

        dat_categories = self.default_config.get("dat_categories", [])

        for d in dat_categories:
            d_sanitized = d.lower().replace(" ", "_")

            if d_sanitized not in file_dict:
                file_dict[d_sanitized] = False

        if all([file_dict[d.lower().replace(" ", "_")] is False for d in dat_categories]):
            file_dict["games"] = True

        return file_dict

    def parse_filename(self, f, file_dict=None):
        """Parse info out of filename"""

        if file_dict is None:
            file_dict = {}

        # Split file into tags
        tags = [f'({x}' for x in f.strip(".zip").split(' (')][1:]

        for regex_key in self.regex:

            regex_type = self.regex[regex_key].get("type", "bool")
            search_tags = self.regex[regex_key].get("search_tags", True)
            group = self.regex[regex_key].get("group", None)
            regex_flags = self.regex[regex_key].get("flags", "I")
            transform_pattern = self.regex[regex_key].get("transform_pattern", None)
            transform_repl = self.regex[regex_key].get("transform_repl", None)

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

            pattern = self.regex[regex_key]["pattern"]

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
