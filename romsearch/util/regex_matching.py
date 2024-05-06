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


def get_bracketed_file_pattern(str_to_match,
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


def get_game_name(f):
    """Get game name, which is just everything up to the first bracket"""

    f = re.findall("^.*?(?=\\s\\()", f)[0]

    return f


def get_short_name(f,
                   regex_config=None,
                   default_config=None,
                   ):
    """Get short game name from the ROM file naming convention"""

    if ".zip" in f:
        f = f.strip(".zip")

    mod_dir = os.path.dirname(romsearch.__file__)

    if default_config is None:
        default_file = os.path.join(mod_dir, "configs", "defaults.yml")
        default_config = load_yml(default_file)

    if regex_config is None:
        regex_file = os.path.join(mod_dir, "configs", "regex.yml")
        regex_config = load_yml(regex_file)

    for regex_key in regex_config:
        regex_type = regex_config[regex_key].get("type", "bool")
        regex_flags = regex_config[regex_key].get("flags", "I")

        pattern = regex_config[regex_key]["pattern"]

        if regex_type == "list":

            if isinstance(default_config[regex_key], dict):
                str_to_join = [default_config[regex_key][key] for key in default_config[regex_key]]
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
