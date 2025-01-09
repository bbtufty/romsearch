import copy
import re
import romsearch
import os

from ..util import load_yml


def get_file_pattern(str_to_match):
    if isinstance(str_to_match, list):
        pattern = "|".join([f"{f}" for f in str_to_match])
    else:
        pattern = f"{str_to_match}.*"

    pattern = f"({pattern})"

    return pattern


def get_bracketed_file_pattern(
    str_to_match,
):
    """Get file pattern to match bracketed things

    This is a little tricky since sometimes things can be matched a little unusually.
    What we do here is allow for matches of letters, commas or spaces before and after,
    but ensure there's no text immediately after the match. So "De" will match for a language
    but not "Demo"
    """

    short_pattern = "[\\s\\-a-zA-Z,0-9]*?,?\\s?{},?\\s?(?![a-zA-Z])[\\s\\-a-zA-Z,0-9]*?"

    if isinstance(str_to_match, list):
        # pattern = "|".join([f".*?{f}.*?" for f in str_to_match])
        pattern = "|".join([short_pattern.replace("{}", f) for f in str_to_match])
    else:
        # pattern = f".*?{str_to_match}.*?"
        pattern = short_pattern.replace("{}", str_to_match)

    pattern = f"\\(({pattern})\\)"

    return pattern


def get_directory_name(f):
    """Get the output directory name, which is just everything up to the first bracket"""

    # Only change things if there is indeed a bracket hidden in there
    f_find = re.findall("^.*?(?=\\s\\()", f)
    if len(f_find) > 0:
        f = f_find[0]

    # Catch the edge case where the directory name can end with
    # a period (e.g. Super Smash Bros.)
    if f.endswith("."):
        f = f[:-1]

    return f


def get_short_name(
    f,
    regex_config=None,
    default_config=None,
):
    """Get short game name from the ROM file naming convention"""

    if ".zip" in f:
        f = f.rstrip(".zip")

    mod_dir = os.path.dirname(romsearch.__file__)

    if default_config is None:
        default_file = os.path.join(mod_dir, "configs", "defaults.yml")
        default_config = load_yml(default_file)

    if regex_config is None:
        regex_file = os.path.join(mod_dir, "configs", "regex.yml")
        regex_config = load_yml(regex_file)

    for regex_key in regex_config:

        # If we have patterns that we do want to keep in the long name, then skip
        include_in_short_title = regex_config[regex_key].get(
            "include_in_short_name", False
        )
        if include_in_short_title:
            continue

        regex_type = regex_config[regex_key].get("type", "bool")
        regex_flags = regex_config[regex_key].get("flags", "I")

        pattern = regex_config[regex_key]["pattern"]

        if regex_type == "list":

            if isinstance(default_config[regex_key], dict):
                str_to_join = [
                    default_config[regex_key][key] for key in default_config[regex_key]
                ]
            else:
                str_to_join = copy.deepcopy(default_config[regex_key])

            pattern = pattern.replace(f"[{regex_key}]", "|".join(str_to_join))

        if regex_flags == "NOFLAG":
            regex_flags = re.NOFLAG
        elif regex_flags == "I":
            regex_flags = re.I
        else:
            raise ValueError("regex_flags should be one of 'NOFLAG', 'I'")

        pattern = f"\\s?{pattern}"

        f = re.sub(pattern=pattern, repl="", string=f, flags=regex_flags)

    return f


def get_region_free_name(
    f,
    regex_config=None,
    default_config=None,
):
    """Get region-free game name from the ROM file naming convention"""

    if ".zip" in f:
        f = f.rstrip(".zip")

    mod_dir = os.path.dirname(romsearch.__file__)

    if default_config is None:
        default_file = os.path.join(mod_dir, "configs", "defaults.yml")
        default_config = load_yml(default_file)

    if regex_config is None:
        regex_file = os.path.join(mod_dir, "configs", "regex.yml")
        regex_config = load_yml(regex_file)

    # We only care about regions and languages here
    regex_config = {
        "regions": regex_config["regions"],
        "languages": regex_config["languages"],
    }

    region_free_name = get_short_name(f, regex_config, default_config)

    return region_free_name
