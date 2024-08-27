import copy
import os
import re

import numpy as np

import romsearch
from ..util import (centred_string,
                    left_aligned_string,
                    setup_logger,
                    load_yml,
                    get_parent_name,
                    get_short_name,
                    load_json
                    )


def get_all_games(files,
                  default_config=None,
                  regex_config=None,
                  ):
    """Get all unique game names from a list of game files."""

    games = [get_short_name(f, default_config=default_config, regex_config=regex_config) for f in files]
    games = list(np.unique(games))

    return games


def get_priority(dupe_dict, parent_name, game_name):
    """Get priority from a dupe dictionary"""

    # First case: parent name doesn't exist in the dupe dict
    if parent_name not in dupe_dict:
        return 1

    # Second case: it does (potentially can be lowercase)
    dupes = [dupe.lower() for dupe in dupe_dict[parent_name]]
    reg_dupes = [dupe for dupe in dupe_dict[parent_name]]

    if game_name.lower() in dupes:
        found_parent_idx = dupes.index(game_name.lower())
        priority = dupe_dict[parent_name][reg_dupes[found_parent_idx]]["priority"]

        return priority

    # Otherwise, just return 1
    return 1


class GameFinder:

    def __init__(self,
                 platform,
                 config_file=None,
                 config=None,
                 default_config=None,
                 regex_config=None,
                 logger=None,
                 log_line_sep="=",
                 log_line_length=100,
                 ):
        """Tool to find games within a list of files

        Will parse through files to get a unique list of games, then pull
        out potential aliases and optionally remove things from user excluded list
        
        Args:
            platform (str): Platform name
            config_file (str, optional): Path to config file. Defaults to None.
            config (dict, optional): Configuration dictionary. Defaults to None.
            default_config (dict, optional): Default configuration dictionary. Defaults to None.
            regex_config (dict, optional): Dictionary of regex config. Defaults to None.
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

        if logger is None:
            log_dir = self.config.get("dirs", {}).get("log_dir", os.path.join(os.getcwd(), "logs"))
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(log_level=log_level,
                                  script_name=f"GameFinder",
                                  log_dir=log_dir,
                                  additional_dir=platform,
                                  )
        self.logger = logger

        # Pull in specifics to include/exclude
        self.include_games = self.config.get("include_games", None)
        self.exclude_games = self.config.get("exclude_games", None)

        # Pull in defaults for finding short game names
        mod_dir = os.path.dirname(romsearch.__file__)

        if default_config is None:
            default_file = os.path.join(mod_dir, "configs", "defaults.yml")
            default_config = load_yml(default_file)
        self.default_config = default_config

        if regex_config is None:
            regex_file = os.path.join(mod_dir, "configs", "regex.yml")
            regex_config = load_yml(regex_file)
        self.regex_config = regex_config

        # Info for dupes
        self.dupe_dir = config.get("dirs", {}).get("dupe_dir", None)
        self.filter_dupes = config.get("gamefinder", {}).get("filter_dupes", True)

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(self,
            files,
            ):

        self.logger.debug(f"{self.log_line_sep * self.log_line_length}")
        self.logger.debug(centred_string("Running GameFinder",
                                        total_length=self.log_line_length)
                         )
        self.logger.debug(f"{self.log_line_sep * self.log_line_length}")

        games_dict = self.get_game_dict(files)
        games_dict = dict(sorted(games_dict.items()))

        self.logger.debug(centred_string(f"Found {len(games_dict)} games",
                                         total_length=self.log_line_length)
                          )
        self.logger.debug(f"{'-' * self.log_line_length}")
        for gi, g in enumerate(games_dict):
            self.logger.debug(left_aligned_string(f"{g}:",
                                                  total_length=self.log_line_length)
                              )

            for ga in games_dict[g]:
                self.logger.debug(left_aligned_string(f"-> Priority {games_dict[g][ga]['priority']}. {ga}",
                                                      total_length=self.log_line_length)
                                  )

            if gi != len(games_dict) - 1:
                self.logger.debug(f"{'-' * self.log_line_length}")

        self.logger.debug(f"{self.log_line_sep * self.log_line_length}")

        return games_dict

    def get_game_dict(self,
                      files,
                      ):

        games = get_all_games(files,
                              default_config=self.default_config,
                              regex_config=self.regex_config,
                              )

        # We need to trim down dupes here. Otherwise, the
        #  dict is just the list we already have
        game_dict = None
        if self.filter_dupes:
            game_dict = self.get_filter_dupes(games)

        # If the dupe filtering has failed, then just assume everything is unique
        if game_dict is None:

            game_dict = {}

            for game in games:
                game_dict[game] = {"priority": 1,
                                   }

        # Remove any excluded files
        if self.exclude_games is not None:
            games_to_remove = self.get_game_matches(game_dict,
                                                    self.exclude_games,
                                                    )
            if games_to_remove is not None:
                for g in games_to_remove:
                    del game_dict[g]

        # Include only included files
        if self.include_games is not None:

            games_to_include = self.get_game_matches(game_dict,
                                                     self.include_games,
                                                     )
            if games_to_include is not None:

                filtered_game_dict = {}
                for g in games_to_include:
                    filtered_game_dict[g] = game_dict[g]

                game_dict = copy.deepcopy(filtered_game_dict)

        return game_dict

    def get_game_matches(self,
                         game_dict,
                         games_to_match,
                         ):
        """Get files that match an input dictionary (so as to properly handle dupes

        Args:
            - game_dict (dict): Dictionary of games to match against
            - games_to_match (list): List of values to match against
        """
        games_matched = []

        if isinstance(games_to_match, dict):
            games_to_match = games_to_match.get(self.platform, None)
        else:
            games_to_match = copy.deepcopy(games_to_match)

        if games_to_match is None:
            return None

        games_matched.extend(games_to_match)

        game_dict_keys = []
        for g in game_dict:
            found_f = False

            for game_matched in games_matched:

                if found_f:
                    continue

                # Look in the group name
                re_find = re.findall(f"^({re.escape(game_matched)}).*", g)

                if len(re_find) > 0:
                    game_dict_keys.append(g)
                    found_f = True

                # If not found, look in the dupe names
                if not found_f:
                    for g_d in game_dict[g]:

                        if found_f:
                            continue

                        re_find = re.findall(f"^({re.escape(game_matched)}).*", g_d)

                        if len(re_find) > 0:
                            game_dict_keys.append(g)
                            found_f = True

        game_dict_keys = np.unique(game_dict_keys)

        if len(game_dict_keys) == 0:
            game_dict_keys = None

        return game_dict_keys

    def get_filter_dupes(self, games):
        """Parse down a list of files based on an input dupe list"""

        if self.dupe_dir is None:
            raise ValueError("dupe_dir must be specified if filtering dupes")

        dupe_file = os.path.join(self.dupe_dir, f"{self.platform} (dupes).json")
        if not os.path.exists(dupe_file):
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(centred_string("No dupe files found",
                                               total_length=self.log_line_length)
                                )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            return None

        game_dict = {}

        dupes = load_json(dupe_file)

        # Loop over games, and the dupes dictionary. Also pull out priority
        for g in games:

            found_parent_name = get_parent_name(game_name=g,
                                                dupe_dict=dupes,
                                                )

            found_parent_name_lower = found_parent_name.lower()
            game_dict_keys = [key for key in game_dict.keys()]
            game_dict_keys_lower = [key.lower() for key in game_dict.keys()]

            if found_parent_name_lower not in game_dict_keys_lower:
                game_dict[found_parent_name] = {}
                final_parent_name = copy.deepcopy(found_parent_name)
            else:
                final_parent_idx = game_dict_keys_lower.index(found_parent_name_lower)
                final_parent_name = game_dict_keys[final_parent_idx]

            priority = get_priority(dupe_dict=dupes, parent_name=found_parent_name, game_name=g)

            game_dict[final_parent_name][g] = {"priority": priority}

        return game_dict
