import copy
import os
import re

import numpy as np

import romsearch
from ..util import setup_logger, load_yml, get_parent_name, get_short_name, create_bar, load_json


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
                 config_file,
                 platform,
                 ):
        """Tool to find games within a list of files

        Will parse through files to get a unique list of games, then pull
        out potential aliases and optionally remove things from user excluded list
        """

        self.logger = setup_logger(log_level="info",
                                   script_name=f"GameFinder",
                                   additional_dir=platform,
                                   )

        if platform is None:
            raise ValueError("platform must be specified")
        self.platform = platform

        config = load_yml(config_file)

        # Pull in specifics to include/exclude
        self.include_games = config.get("include_games", None)
        self.exclude_games = config.get("exclude_games", None)

        # Pull in defaults for finding short game names
        mod_dir = os.path.dirname(romsearch.__file__)
        default_file = os.path.join(mod_dir, "configs", "defaults.yml")
        self.default_config = load_yml(default_file)

        regex_file = os.path.join(mod_dir, "configs", "regex.yml")
        self.regex_config = load_yml(regex_file)

        # Info for dupes
        self.dupe_dir = config.get("dupe_dir", None)
        self.filter_dupes = config.get("gamefinder", {}).get("filter_dupes", True)

    def run(self,
            files,
            ):

        self.logger.info(create_bar(f"START GameFinder"))

        games_dict = self.get_game_dict(files)
        games_dict = dict(sorted(games_dict.items()))

        self.logger.info(f"Found {len(games_dict)} games:")
        for g in games_dict:
            self.logger.info(f"{g}: {games_dict[g]}")

        return games_dict

    def get_game_dict(self,
                      files,
                      ):

        games = get_all_games(files,
                              default_config=self.default_config,
                              regex_config=self.regex_config,
                              )

        # Remove any excluded files
        if self.exclude_games is not None:
            games_to_remove = self.get_game_matches(games,
                                                    self.exclude_games,
                                                    )

            if games_to_remove is not None:
                for i in sorted(games_to_remove, reverse=True):
                    games.pop(i)

        # Include only included files
        if self.include_games is not None:
            games_to_include = self.get_game_matches(games,
                                                     self.include_games,
                                                     )
            if games_to_include is not None:
                games = np.asarray(games)[games_to_include]

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

        return game_dict

    def get_game_matches(self, files, games_to_match):
        """Get files that match an input list (games_to_match)"""
        games_matched = []

        if isinstance(games_to_match, dict):
            games_to_match = games_to_match.get(self.platform, None)
        else:
            games_to_match = copy.deepcopy(games_to_match)

        if games_to_match is None:
            return None

        games_matched.extend(games_to_match)

        idx = []
        for i, f in enumerate(files):
            found_f = False
            # Search within each item since the matches might not be exact
            for game_matched in games_matched:

                if found_f:
                    continue

                re_find = re.findall(f"{game_matched}*", f)

                if len(re_find) > 0:
                    idx.append(i)
                    found_f = True

        return idx

    def get_filter_dupes(self, games):
        """Parse down a list of files based on an input dupe list"""

        if self.dupe_dir is None:
            raise ValueError("dupe_dir must be specified if filtering dupes")

        dupe_file = os.path.join(self.dupe_dir, f"{self.platform} (dupes).json")
        if not os.path.exists(dupe_file):
            self.logger.warning("No dupe files found")
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
