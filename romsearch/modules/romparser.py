import copy
import os
import re
from packaging.version import Version

import romsearch
from ..util import (
    centred_string,
    left_aligned_string,
    setup_logger,
    get_file_time,
    load_yml,
    load_json,
    match_retool_search_terms,
    get_short_name,
)

DICT_DEFAULT_VALS = {"bool": False, "str": "", "list": []}
USE_TITLE_POS = [
    "languages",
]


def find_pattern(regex, search_str, group_number=0):
    """
    Take a regex pattern and find potential matches within a search string
    """
    regex_search_str = None

    regex_search = re.search(regex, search_str)
    if regex_search:
        regex_search_str = regex_search.group(group_number)

    return regex_search_str


def get_pattern_val(
    regex,
    tag,
    regex_type,
    pattern_mappings=None,
    title_pos=None,
    use_title_pos=False,
):
    """Get values out from a regex pattern, optionally mapping back to something more readable for lists

    Args:
        regex: Regex pattern
        tag: Found tag
        regex_type: Regex pattern type. Can be str, bool, list
        pattern_mappings: Mapping from regex pattern to more readable values
        title_pos: Position of title for compilations. Defaults to None
        use_title_pos: Use title_pos? Defaults to False
    """

    pattern_string = find_pattern(regex, tag)

    if pattern_string is not None:
        pattern_string = pattern_string.strip("()")

        # Split out to the specific languages, but only if they're marked correctly
        if title_pos is not None and use_title_pos and "+" in pattern_string:
            pattern_string = pattern_string.split("+")[title_pos - 1]

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

def apply_filters(
        file_dict,
):
    """Apply any filters we may have

    Args:
        file_dict (dict): Dictionary of file properties
    """

    # Flag supersets
    flag_as_superset = file_dict.get("flag_as_superset", None)
    if flag_as_superset is not None:
        file_dict["flag_as_superset"] = flag_as_superset

    return file_dict


def is_ra_subset(name):
    """Check if a name is a RetroAchievements subset

    Args:
        name (str): Name to check
    """

    match_pattern = "\\[Subset.*\\]"

    match = find_pattern(match_pattern, name)
    is_subset = False
    if match is not None:
        is_subset = True

    return is_subset


def check_match(i, j, checks_passed=None):
    """Check if two bools/strings/lists match

    For lists, we simply check if there's any subset that matches

    Args:
        i: Input 1
        j: Input 2
        checks_passed: If not None, will inherit this as initial start.
            Else, will default to True
    """

    if checks_passed is None:
        checks_passed = True
    if not isinstance(checks_passed, bool):
        raise ValueError("checks_passed should be a boolean value")

    # If we have a bool or string, then they should match
    if isinstance(i, bool) or isinstance(i, str):
        if not i == j:
            checks_passed = False

    # If a list, then check there's at least some overlap
    elif isinstance(i, list):
        s_i = set(i)
        s_j = set(j)
        s_k = s_i.intersection(s_j)

        if len(s_k) == 0:
            checks_passed = False

    else:
        t = type(i)
        raise ValueError(f"Do not know how to check against type {t}")

    return checks_passed


def set_english_friendly(
    file_dict,
):
    """Set English as a language if English-friendly is flagged"""

    # Only change things if we're flagged
    is_english_friendly = file_dict.get("english_friendly", False)

    if not is_english_friendly:
        return file_dict

    if "English" not in file_dict["languages"]:
        file_dict["languages"].append("English")

    return file_dict


class ROMParser:

    def __init__(
        self,
        platform,
        game,
        dat=None,
        retool=None,
        ra_hashes=None,
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
            dat (dict): Parsed dat dictionary. Defaults to None, which will try to load the dat file if it exists
            retool (dict): Retool dictionary. Defaults to None, which will try to load the file if it exists
            ra_hashes (dict): RA hash dictionary. Defaults to None, which will try to load the file if it exists
            config_file (str, optional): path to config file. Defaults to None.
            config (dict, optional): configuration dictionary. Defaults to None.
            platform_config (dict, optional): platform configuration dictionary. Defaults to None.
            default_config (dict, optional): default configuration dictionary. Defaults to None.
            regex_config (dict, optional): regex configuration dictionary. Defaults to None.
            logger (logging.Logger, optional): logger instance. Defaults to None.
            log_line_length (int, optional): Line length of log. Defaults to 100

        TODO:
            For the RetroAchievements, there are hacks and unlicensed stuff that seems to work differently
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
            log_dir = self.config.get("dirs", {}).get(
                "log_dir", os.path.join(os.getcwd(), "logs")
            )
            logger_add_dir = str(os.path.join(platform, game))
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(
                log_level=log_level,
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

        self.ra_file_exts = self.default_config.get("ra_file_exts", [])
        self.ra_labels = self.default_config.get("ra_labels", [])
        self.ra_patch_checks = self.default_config.get("ra_patch_checks", [])

        if regex_config is None:
            regex_file = os.path.join(mod_dir, "configs", "regex.yml")
            regex_config = load_yml(regex_file)
        self.regex_config = regex_config

        if platform_config is None:
            platform_config_file = os.path.join(
                mod_dir, "configs", "platforms", f"{platform}.yml"
            )
            platform_config = load_yml(platform_config_file)
        self.platform_config = platform_config

        self.raw_dir = self.config.get("dirs", {}).get("raw_dir", None)
        if not self.raw_dir:
            raise ValueError("raw_dir must be specified in config.yml")

        self.use_dat = self.config.get("romparser", {}).get("use_dat", True)
        self.use_retool = self.config.get("romparser", {}).get("use_retool", True)
        self.use_ra_hashes = self.config.get("romparser", {}).get(
            "use_ra_hashes", False
        )
        self.use_filename = self.config.get("romparser", {}).get("use_filename", True)
        self.dry_run = self.config.get("romparser", {}).get("dry_run", False)

        # If we're using the dat file, pull it out here
        self.dat = dat
        if self.use_dat and self.dat is None:
            dat_dir = self.config.get("dirs", {}).get("parsed_dat_dir", None)
            if dat_dir is None:
                raise ValueError("parsed_dat_dir must be specified in config.yml")
            dat_file = os.path.join(dat_dir, f"{platform} (dat parsed).json")
            if os.path.exists(dat_file):
                self.dat = load_json(dat_file)

        # If we're using the retool file, pull it out here
        self.retool = retool
        if self.use_retool and self.retool is None:
            dat_dir = self.config.get("dirs", {}).get("parsed_dat_dir", None)
            if dat_dir is None:
                raise ValueError("parsed_dat_dir must be specified in config.yml")
            retool_file = os.path.join(dat_dir, f"{platform} (retool).json")
            if os.path.exists(retool_file):
                retool = load_json(retool_file)
                self.retool = retool["variants"]

        # If we're using the RA hashes, pull it out here
        self.ra_hashes = ra_hashes
        if self.use_ra_hashes and self.ra_hashes is None:
            ra_hash_dir = self.config.get("dirs", {}).get("ra_hash_dir", None)
            if ra_hash_dir is None:
                raise ValueError("ra_hash_dir must be specified in config.yml")
            ra_hash_file = os.path.join(ra_hash_dir, f"{platform}.json")
            if os.path.exists(ra_hash_file):
                self.ra_hashes = load_json(ra_hash_file)

        self.hash_method = self.platform_config.get("ra_hash_method", None)

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(
        self,
        files,
    ):
        """Run the ROM parser"""

        game_dict = copy.deepcopy(files)

        self.logger.debug(f"{self.log_line_sep * self.log_line_length}")
        self.logger.debug(
            centred_string(
                f"Running ROMParser for {self.game}", total_length=self.log_line_length
            )
        )
        self.logger.debug(f"{self.log_line_sep * self.log_line_length}")

        for f in files:
            # # Get the potential title position out for compilations
            title_pos = files[f].get("title_pos", None)

            f_parsed = self.parse_file(
                f=f,
                file_dict=copy.deepcopy(files[f]),
                title_pos=title_pos,
            )
            game_dict[f].update(f_parsed)

        return game_dict

    def parse_file(
        self,
        f=None,
        file_dict=None,
        title_pos=None,
    ):
        """Parse useful info out of a specific file

        Args:
            f (str): Filename. Will only use this if something more suitable isn't found
            file_dict (dict): Dictionary of file properties
            title_pos (int, optional): Title position for compilations. Defaults to None.
        """

        if file_dict is None:
            file_dict = {}

        if self.use_filename:
            file_dict = self.parse_filename(
                f=f,
                file_dict=file_dict,
                title_pos=title_pos,
            )

        if self.use_retool:
            file_dict = self.parse_retool(file_dict=file_dict)

        if self.use_dat:
            file_dict = self.parse_dat(
                f=f,
                file_dict=file_dict,
            )

        # Apply any filters that wouldn't have been applied here
        file_dict = apply_filters(file_dict)

        file_dict["has_cheevos"] = False
        file_dict["patch_file"] = ""

        if self.use_ra_hashes:
            file_dict = self.parse_ra_hashes(
                file_dict=file_dict,
            )

        # Any last minute finalisations
        self.finalise_file_dict(file_dict)

        # File modification time
        full_file_path = os.path.join(
            self.raw_dir, self.platform, file_dict.get("original_name", f)
        )
        file_time = get_file_time(
            full_file_path,
            datetime_format=self.default_config["datetime_format"],
        )
        file_dict["file_mod_time"] = file_time

        # Log out these tags in a nice readable way
        self.logger.debug(centred_string(f"{f}:", total_length=self.log_line_length))

        # Track the various tags we can have
        true_tags = []
        false_tags = []
        none_tags = []
        str_tags = {}
        int_tags = {}
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
            elif isinstance(file_dict[key], int):
                int_tags[key] = file_dict[key]
            elif file_dict[key] is None:
                none_tags.append(key)
            else:
                raise ValueError(
                    f"{file_dict[key]} is not something I know how to parse"
                )

        # Log the string tags
        self.logger.debug(
            left_aligned_string(f"String tags:", total_length=self.log_line_length)
        )
        for tag in str_tags:
            if str_tags[tag] == "":
                continue
            self.logger.debug(
                left_aligned_string(
                    f"-> {tag}: {str_tags[tag]}", total_length=self.log_line_length
                )
            )

        # Log the list tags
        self.logger.debug(
            left_aligned_string(f"List tags:", total_length=self.log_line_length)
        )
        for tag in list_tags:
            if not list_tags[tag]:
                continue
            self.logger.debug(
                left_aligned_string(
                    f"-> {tag}: {', '.join(str(i) for i in list_tags[tag])}",
                    total_length=self.log_line_length,
                )
            )

        # Log the list tags
        self.logger.debug(
            left_aligned_string(f"Number tags:", total_length=self.log_line_length)
        )
        for tag in int_tags:
            self.logger.debug(
                left_aligned_string(
                    f"-> {tag}: {int_tags[tag]}",
                    total_length=self.log_line_length,
                )
            )

        # Log the True bool tags
        self.logger.debug(
            left_aligned_string(f"Tagged:", total_length=self.log_line_length)
        )
        for tag in true_tags:
            self.logger.debug(
                left_aligned_string(f"-> {tag}", total_length=self.log_line_length)
            )

        # Log the False bool tags
        self.logger.debug(
            left_aligned_string(f"Not tagged:", total_length=self.log_line_length)
        )
        for tag in false_tags:
            self.logger.debug(
                left_aligned_string(f"-> {tag}", total_length=self.log_line_length)
            )

        # Log any None tags
        self.logger.debug(
            left_aligned_string(f"None:", total_length=self.log_line_length)
        )
        for tag in none_tags:
            self.logger.debug(
                left_aligned_string(f"-> {tag}", total_length=self.log_line_length)
            )

        self.logger.debug(f"{'-' * self.log_line_length}")

        return file_dict

    def parse_retool(self, file_dict=None):
        """Parse info out of the retool file"""

        if file_dict is None:
            file_dict = {}

        if self.retool is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    f"No retool file found for {self.platform}. Skipping",
                    total_length=self.log_line_length,
                )
            )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            return file_dict

        # Loop over the variants, see if we get a match
        found_cat = False
        for retool_dict in self.retool:

            if found_cat:
                continue

            # If we don't have titles within the dupe dict, skip
            if "titles" not in retool_dict:
                continue

            # Match properly given search terms
            full_name = copy.deepcopy(file_dict["full_name"])
            short_name = copy.deepcopy(file_dict["short_name"])
            region_free_name = copy.deepcopy(file_dict["region_free_name"])

            for t in retool_dict["titles"]:
                search_term = t["searchTerm"]
                match_type = t.get("nameType", None)

                found_retool_variant = match_retool_search_terms(
                    full_name=full_name,
                    search_term=search_term,
                    short_name=short_name,
                    region_free_name=region_free_name,
                    match_type=match_type,
                )

                if found_retool_variant:
                    retool_cats = retool_dict.get("categories", [])
                    for retool_cat in retool_cats:
                        file_cat = retool_cat.lower().replace(" ", "_")
                        file_dict[file_cat] = True

        return file_dict

    def parse_dat(
        self,
        f=None,
        file_dict=None,
    ):
        """Parse info out of the dat file

        Args:
            f (str): Fallback filename
            file_dict (dict): Dictionary of file info
        """

        if file_dict is None:
            file_dict = {}

        f = copy.deepcopy(file_dict.get("original_name", f))

        if self.dat is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    f"No dat file found for {self.platform}. Skipping",
                    total_length=self.log_line_length,
                )
            )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            return file_dict

        # Remember there aren't zips in the dat entries
        dat_entry = self.dat.get(f.rstrip(".zip"), None)
        if not dat_entry:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    f"No dat entry found for {f}. Skipping",
                    total_length=self.log_line_length,
                )
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

        # Get the checksums out
        checksums = self.default_config.get("dat_checksums", [])
        for checksum in checksums:

            # Because sometimes we have multiple files within the ROM, loop over and append them all
            rom_entries = dat_entry.get("rom", [])
            if isinstance(rom_entries, dict):
                rom_entries = [rom_entries]

            for rom_entry in rom_entries:

                if checksum in rom_entry:
                    if checksum not in file_dict:
                        file_dict[checksum] = []

                    file_dict[checksum].append(rom_entry[checksum])

        return file_dict

    def parse_ra_hashes(
        self,
        file_dict=None,
    ):
        """See if we can find ROMs that support RetroAchievements

        Note that this requires a bunch of parsing to have already occurred
        """

        # If we don't have a dictionary already, then this won't work
        if file_dict is None:
            file_dict = {}
            return file_dict

        if self.hash_method is None:
            self.logger.warning(
                centred_string(
                    f"RA hash method not defined for {self.platform}",
                    total_length=self.log_line_length,
                )
            )
            return file_dict

        file_dict = self.match_hashes(file_dict)

        return file_dict

    def match_hashes(
        self,
        file_dict,
    ):
        """Get whether ROM has cheevos by various potential hash methods

        Args:
            f (str): Filename
            file_dict (dict): Dictionary of ROM descriptions
        """

        has_cheevos = False
        patch_file = ""

        if self.hash_method not in ["md5", "custom"]:
            self.logger.warning(
                centred_string(
                    f"Cannot currently handle {self.hash_method} hash method",
                    total_length=self.log_line_length,
                )
            )
            return has_cheevos, patch_file

        ra_dict = self.get_ra_dict()

        # Get the potential RA match by name (this won't include potentially patched ROMs)
        has_cheevos, patch_file = self.get_ra_match(
            file_dict=file_dict,
            ra_dict=ra_dict,
        )

        # If we've found something, stop here
        if has_cheevos:
            file_dict["has_cheevos"] = has_cheevos
            file_dict["patch_file"] = patch_file
            return file_dict

        # If we're on a custom hash, and we haven't found anything, now look
        # via parsing the names
        if self.hash_method == "custom":
            has_cheevos, patch_file = self.get_parsed_match(
                file_dict=file_dict, ra_dict=ra_dict, want_patched_files=False
            )
            if has_cheevos:
                file_dict["has_cheevos"] = has_cheevos
                file_dict["patch_file"] = patch_file
                return file_dict

        # If we still haven't, now look through files to see if we just need
        # a patch (i.e. the hash will change, but we have the file)
        has_cheevos, patch_file = self.get_parsed_match(
            file_dict=file_dict,
        )

        file_dict["has_cheevos"] = has_cheevos
        file_dict["patch_file"] = patch_file

        return file_dict

    def get_ra_dict(
        self,
    ):
        """Get a big dictionary of RA hashes with useful info"""

        # Pull out the particular key we need
        if self.hash_method == "md5":
            key = "MD5"
        elif self.hash_method == "custom":
            key = "Name"
        else:
            raise ValueError(f"Cannot currently handle {self.hash_method} hash method")

        # Because of inconsistencies between naming schemes, just pull a huge dictionary out here rather than try
        # to be clever
        ra_dict = {}

        for r in self.ra_hashes:
            for h in self.ra_hashes[r]["Hashes"]:

                # If the RA list is a subset, then skip
                if is_ra_subset(r):
                    continue

                # Use the md5 as the unique key, and then name as the thing we'll match to.
                # Ensure we lowercase the hash, just to be sure
                md5 = copy.deepcopy(h["MD5"].lower())
                id_name = copy.deepcopy(h[key])
                id_name = id_name.strip()

                # Also just pull out the ROM name, since we need that later
                rom_name = copy.deepcopy(h["Name"])
                rom_name = rom_name.strip()

                # Ensure we also lowercase the hash here, if we need to
                if key in ["MD5"]:
                    id_name = id_name.lower()

                # If we're dealing with names, there might
                # be file extensions to strip
                if key in ["Name"]:
                    for ext in self.ra_file_exts:
                        if id_name.endswith(ext):
                            id_name = id_name.rstrip(ext)

                # FIXME: Here as a catch-all, hopefully won't be a problem
                if md5 in ra_dict:
                    raise ValueError(f"Hash {md5} multiply defined")

                ra_dict[md5] = {
                    "name": id_name,
                    "full_name": rom_name,
                    "dir_name": rom_name.split(" (")[0],
                    "patch_url": h["PatchUrl"],
                }

        return ra_dict

    def get_ra_match(
        self,
        file_dict,
        ra_dict=None,
    ):
        """Match a file to RetroAchievements supported files

        Args:
            file_dict (dict): Dictionary of ROM descriptions
            ra_dict (dict): Dictionary of RA hashes
        """

        has_cheevos = False
        patch_file = ""

        # Pull out the particular key we need
        if self.hash_method == "md5":
            match_list = file_dict.get("md5", [])
        elif self.hash_method == "custom":
            match_list = [file_dict["original_name"].rstrip(".zip")]
        else:
            self.logger.warning(
                centred_string(
                    f"Cannot currently handle {self.hash_method} hash method",
                    total_length=self.log_line_length,
                )
            )
            return has_cheevos, patch_file

        # If we've got nothing, don't waste time
        if len(match_list) == 0:
            return has_cheevos, patch_file

        if ra_dict is None:
            ra_dict = self.get_ra_dict()

        # Again, if there's nothing here just return
        if len(ra_dict) == 0:
            return has_cheevos, patch_file

        for m in match_list:
            for r in ra_dict:
                if m == ra_dict[r]["name"]:
                    has_cheevos = True
                    patch_file = ra_dict[r]["patch_url"]

        if patch_file is None:
            patch_file = ""

        return has_cheevos, patch_file

    def get_parsed_match(
        self,
        file_dict,
        ra_dict=None,
        want_patched_files=True,
    ):
        """Match a file to RetroAchievements supported files that potentially need patches

        Args:
            file_dict (dict): Dictionary of ROM descriptions
            ra_dict (dict): Dictionary of RA hashes
            want_patched_files (bool): Whether we're looking for hashes with patches or not. Defaults to True
        """

        has_cheevos = False
        patch_file = ""

        if ra_dict is None:
            ra_dict = self.get_ra_dict()

        # Again, if there's nothing here just return
        if len(ra_dict) == 0:
            return has_cheevos, patch_file

        multiple_patch_files_found = False

        for r in ra_dict:

            # If we want patch files, and we don't have them, skip
            if want_patched_files and ra_dict[r]["patch_url"] is None:
                continue

            if multiple_patch_files_found:
                continue

            # Start by ensuring the names up to first bracket at least match
            if file_dict["dir_name"] == ra_dict[r]["dir_name"]:

                r_parsed = self.parse_filename(f=ra_dict[r]["full_name"])

                # If we're a superset, then ensure the short names also match, since
                # we need to be more stringent
                is_superset = file_dict.get("is_superset", False)
                ra_dict_short_name = get_short_name(
                    ra_dict[r]["full_name"],
                    regex_config=self.regex_config,
                    default_config=self.default_config,
                )
                if is_superset and not file_dict["short_name"] == ra_dict_short_name:
                    continue

                # Force some version info in here, if the RA name doesn't have it
                if r_parsed["version_no"] == "" and file_dict["version_no"] != "":
                    if Version(file_dict["version_no"]) == Version("1"):
                        r_parsed["version_no"] = copy.deepcopy(file_dict["version_no"])

                # Now, make sure all the useful checks pass
                ra_checks_passed = True
                for check in self.ra_patch_checks:

                    # If we've already failed, then just skip
                    if not ra_checks_passed:
                        continue

                    ra_checks_passed = check_match(
                        file_dict[check],
                        r_parsed[check],
                        checks_passed=ra_checks_passed,
                    )

                    # After this first pass, also see if any of the regex checks are grouped,
                    # and double-check the sublevel below. This is because we could have e.g.
                    # mismatched modern types (like a GameCube version vs a Wii U Virtual Console
                    # version), which inevitably won't match hashes
                    if ra_checks_passed:
                        if check not in self.regex_config:
                            for r_c in self.regex_config:

                                if not ra_checks_passed:
                                    continue

                                r_c_group = self.regex_config[r_c].get("group", None)
                                if r_c_group == check:
                                    ra_checks_passed = check_match(
                                        file_dict[r_c],
                                        r_parsed[r_c],
                                        checks_passed=ra_checks_passed,
                                    )

                if ra_checks_passed:

                    # If we seem to have multiple patch files defined,
                    # then raise a warning and assume there isn't a patch
                    if patch_file != "":
                        self.logger.warning(
                            centred_string(
                                f"Multiple potential patch files found for {file_dict['original_name']}",
                                total_length=self.log_line_length,
                            )
                        )
                        has_cheevos = False
                        patch_file = None
                        multiple_patch_files_found = True

                    else:
                        has_cheevos = True
                        patch_file = ra_dict[r]["patch_url"]

                    if patch_file is None:
                        patch_file = ""

        if patch_file is None:
            patch_file = ""

        return has_cheevos, patch_file

    def finalise_file_dict(
        self,
        file_dict,
    ):
        """Do any last minute finalisation to the file dict"""

        file_dict = self.set_game_category(file_dict)
        file_dict = self.set_implicit_languages(file_dict)
        file_dict = set_english_friendly(file_dict)

        return file_dict

    def set_game_category(
        self,
        file_dict,
    ):
        """If a dat category hasn't been set, set it to game"""

        dat_categories = self.default_config.get("dat_categories", [])

        for d in dat_categories:
            d_sanitized = d.lower().replace(" ", "_")

            if d_sanitized not in file_dict:
                file_dict[d_sanitized] = False

        if all(
            [file_dict[d.lower().replace(" ", "_")] is False for d in dat_categories]
        ):
            file_dict["games"] = True

        return file_dict

    def set_implicit_languages(
        self,
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

    def parse_filename(
        self,
        f=None,
        file_dict=None,
        title_pos=None,
    ):
        """Parse info out of filename

        Args:
            f (str): filename. Defaults to None, which will pull the original
                name out of the dict
            title_pos (int): Title position for compilations. Defaults to None
            file_dict (dict): Existing file dictionary. Defaults to None, which
                will create an empty one
        """

        if file_dict is None:
            file_dict = {}

        if "full_name" not in file_dict and f is None:
            raise ValueError(
                "Either f needs to be defined, or full_name needs to be in the file dictionary"
            )

        if f is None:
            # Pull the filename out, which is the full name
            f = copy.deepcopy(file_dict["full_name"])

        # Split file into tags
        tags = [f"({x}" for x in f.rstrip(".zip").split(" (")][1:]

        for regex_key in self.regex_config:

            # Are we potentially using the title position?
            use_title_pos = False
            if regex_key in USE_TITLE_POS:
                use_title_pos = True

            regex_type = self.regex_config[regex_key].get("type", "bool")
            search_tags = self.regex_config[regex_key].get("search_tags", True)
            group = self.regex_config[regex_key].get("group", None)
            regex_flags = self.regex_config[regex_key].get("flags", "I")
            transform_pattern = self.regex_config[regex_key].get(
                "transform_pattern", None
            )
            transform_repl = self.regex_config[regex_key].get("transform_repl", None)

            dict_default_val = DICT_DEFAULT_VALS.get(regex_type, None)
            if dict_default_val is None:
                raise ValueError(
                    f"regex_type should be one of {list(DICT_DEFAULT_VALS.keys())}"
                )

            if regex_key not in file_dict:
                file_dict[regex_key] = copy.deepcopy(dict_default_val)

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
                    str_to_join = [
                        self.default_config[regex_key][key]
                        for key in self.default_config[regex_key]
                    ]
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

                    pattern_string = get_pattern_val(
                        regex,
                        tag,
                        regex_type,
                        pattern_mappings=pattern_mappings,
                        title_pos=title_pos,
                        use_title_pos=use_title_pos,
                    )
                    if pattern_string is not None:

                        if transform_pattern is not None:
                            pattern_string = re.sub(
                                transform_pattern, transform_repl, pattern_string
                            )

                        file_dict[regex_key] = pattern_string
                        found_tag = True
            else:
                pattern_string = get_pattern_val(
                    regex,
                    f,
                    regex_type,
                    pattern_mappings=pattern_mappings,
                    title_pos=title_pos,
                    use_title_pos=use_title_pos,
                )
                if pattern_string is not None:
                    file_dict[regex_key] = pattern_string

            # Update groups, if needed
            if group is not None:

                # We can have multiple groups per-tag, so take that into account
                if isinstance(group, str):
                    group = [group]

                for g in group:

                    if g not in file_dict:
                        file_dict[g] = dict_default_val

                    if regex_type == "bool":
                        file_dict[g] = file_dict[g] | file_dict[regex_key]
                    elif regex_type == "str":
                        if file_dict[g] and file_dict[regex_key]:
                            raise ValueError("Can't combine multiple groups with type str")
                        else:
                            file_dict[g] += file_dict[regex_key]
                    elif regex_type == "list":
                        file_dict[g].extend(file_dict[regex_key])
                    else:
                        raise ValueError(
                            f"regex_type should be one of {list(DICT_DEFAULT_VALS.keys())}"
                        )

        return file_dict
