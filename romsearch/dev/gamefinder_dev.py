import logging
import os

import romsearch
from romsearch import GameFinder
from ..util import (
    get_short_name,
    load_json,
    load_yml,
    get_directory_name,
    normalize_name,
    get_region_free_name,
)


def check_regex_parsing(dat_filename):
    """Run a .dat file through the short name parser

    This is useful when adding a new platform, so we can see
    what new terms need to be added
    """

    dat_file = load_json(dat_filename)
    all_files = [f for f in dat_file]
    all_files.sort()

    mod_dir = os.path.dirname(romsearch.__file__)

    default_config_file = os.path.join(mod_dir, "configs", "defaults.yml")
    default_config = load_yml(default_config_file)

    default_config = default_config

    regex_config_file = os.path.join(mod_dir, "configs", "regex.yml")
    regex_config = load_yml(regex_config_file)

    regex_config = regex_config

    # Parse all the names in the dat file
    all_file_dict = {}
    for f in all_files:

        dir_name = get_directory_name(f)
        full_name = normalize_name(
            f,
            disc_rename=default_config["disc_rename"],
        )
        short_name = get_short_name(
            full_name,
            regex_config=regex_config,
            default_config=default_config,
        )
        region_free_name = get_region_free_name(
            full_name,
            regex_config=regex_config,
            default_config=default_config,
        )

        all_file_dict[f] = {
            "original_name": f,
            "dir_name": dir_name,
            "full_name": full_name,
            "short_name": short_name,
            "region_free_name": region_free_name,
            "matched": False,
        }

    return all_file_dict


def parse_games_from_dat(
    config_file,
    platform,
):
    """Using a config file and platform, parse all the games from a dat

    This will include the dupe parsing and everything if specified in the config
    """

    config = load_yml(config_file)

    parsed_dat_dir = config.get("dirs", {}).get("parsed_dat_dir", None)

    if parsed_dat_dir is None:
        raise ValueError("No parsed_dat_dir found in config file")

    dat_filename = os.path.join(parsed_dat_dir, f"{platform} (dat parsed).json")

    if not os.path.exists(dat_filename):
        raise ValueError("No parsed dat file found")

    all_file_dict = check_regex_parsing(dat_filename)

    finder = GameFinder(
        config_file=config_file,
        platform=platform,
    )
    finder.logger.setLevel(logging.WARNING)

    all_games = finder.run(files=all_file_dict)

    return all_games
