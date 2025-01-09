import copy
import numpy as np
import os
import re
from iso639 import Lang

import romsearch
from .romparser import ROMParser
from ..util import (
    centred_string,
    left_aligned_string,
    setup_logger,
    load_yml,
    load_json,
    match_retool_search_terms,
    get_directory_name,
)

DUPE_DEFAULT = {
    "is_compilation": False,
    "name_type": None,
    "priority": 1,
    "title_pos": None,
    "filters": None,
}


def check_regions(
    filter_regions,
    rom_regions,
):
    """Check condition regions against parsed regions

    Here, we only check that any of the ROM regions match any of the
    filter regions

    Args:
        filter_regions (list): List of regions to match from the filter
        rom_regions (list): Parsed ROM regions
    """

    s_f = set(filter_regions)
    s_r = set(rom_regions)

    s_i = s_r.intersection(s_f)

    # If we've got no matches, then this hasn't been satisfied
    if len(s_i) == 0:
        return False

    return True


def check_languages(
    filter_langs,
    rom_langs,
):
    """Check condition languages against parsed languages

    Here, we only check that any of the ROM languages match any of the
    filter languages. N.B. retool here uses ISO 639-1, so we need to
    parse them

    Args:
        filter_langs (list): List of languages to match from the filter
        rom_langs (list): Parsed ROM languages
    """

    long_filter_langs = [Lang(fl.lower()).name for fl in filter_langs]

    s_f = set(long_filter_langs)
    s_r = set(rom_langs)

    s_i = s_r.intersection(s_f)

    # If we've got no matches, then this hasn't been satisfied
    if len(s_i) == 0:
        return False

    return True


def check_string(
    regex_str,
    file_name,
):
    """Check filename for regex string

    Args:
        regex_str (str): String to check
        file_name (str): Name of file to check
    """

    match = re.search(regex_str, file_name)

    if match is None:
        return False

    return True


def check_region_order(
    region_order,
    user_region_preferences,
    all_regions=None,
):
    """Check region order against parsed regions

    Here, we only check that *any* of the higher regions are
    higher in user preference than *all* of the lower regions

    Args:
        region_order (dict): Dictionary of form {"higherRegions": [], "lowerRegions": []}
        user_region_preferences (list): Ordered list of user region preferences
        all_regions (list): List of all available regions
    """

    if all_regions is None:
        all_regions = []

    higher_regions = region_order["higherRegions"]
    lower_regions = region_order["lowerRegions"]

    # If we've got an 'all other regions' here, then
    # pull them out
    updated_higher_regions = copy.deepcopy(higher_regions)
    if higher_regions == ["All other regions"]:
        updated_higher_regions = copy.deepcopy(all_regions)
        for reg in lower_regions:
            updated_higher_regions.remove(reg)

    updated_lower_regions = copy.deepcopy(lower_regions)
    if lower_regions == ["All other regions"]:
        updated_lower_regions = copy.deepcopy(all_regions)
        for reg in higher_regions:
            updated_lower_regions.remove(reg)

    higher_regions = copy.deepcopy(updated_higher_regions)
    lower_regions = copy.deepcopy(updated_lower_regions)

    high_prio_region = 99
    for reg in higher_regions:

        # If we have the region in the preferences, note the location
        if reg in user_region_preferences:

            # Take the highest priority
            high_prio_region = min(
                [high_prio_region, user_region_preferences.index(reg)]
            )

    # If we still have a high priority of 99, we haven't found anything so jump out
    if high_prio_region == 99:
        return False

    # Now look through the low priorities, and find the highest priority of those
    low_prio_region = 99
    for reg in lower_regions:

        # If we have the region in the preferences, note the location
        if reg in user_region_preferences:

            # Take the highest priority
            low_prio_region = min([low_prio_region, user_region_preferences.index(reg)])

    # If we're at a low priority of 99, then we haven't found anything so we're good to
    # return a True
    if low_prio_region == 99:
        return True

    # If *any* of the high priority regions are higher than *all* of the low
    # priority, then return True. Else, False
    if low_prio_region > high_prio_region:
        return False

    return True


def add_dupe_entry_to_game_dict(
    game,
    game_dict,
    parent,
):
    """Add a dupe entry to the game dict

    Args:
        game (dict): Dictionary containing various game names
        game_dict (dict): Dictionary of games. Defaults
            to None, which will create an empty dict
        parent: Parent for the game. Can either
            be a string, which will set up a default
            dictionary for the parent, or a dictionary
            to inherit
    """

    game_name = copy.deepcopy(game["original_name"])

    if isinstance(parent, str):
        parent_name = copy.deepcopy(parent)
        dupe_entry = DUPE_DEFAULT
    elif isinstance(parent, dict):
        parent_name = parent["parent_name"]
        dupe_entry = parent["dupe_entry"]
    else:
        raise ValueError(f"parent should be one of str, dict")

    # Update the directory name, so that it matches the short parent name
    new_dir_name = get_directory_name(parent_name)
    game["dir_name"] = copy.deepcopy(new_dir_name)

    parent_name_lower = parent_name.lower()
    game_dict_keys = [key for key in game_dict.keys()]
    game_dict_keys_lower = [key.lower() for key in game_dict.keys()]

    if parent_name_lower not in game_dict_keys_lower:
        game_dict[parent_name] = {}
        final_parent_name = copy.deepcopy(parent_name)
    else:
        final_parent_idx = game_dict_keys_lower.index(parent_name_lower)
        final_parent_name = game_dict_keys[final_parent_idx]

    # We want to make sure we also don't duplicate on the names being upper/lowercase
    g_names = [g_dict for g_dict in game_dict[final_parent_name]]
    g_names_lower = [g_name.lower() for g_name in g_names]
    if game_name.lower() in g_names_lower:
        g_idx = g_names_lower.index(game_name.lower())
        game_name = g_names[g_idx]

    if game_name not in game_dict[final_parent_name]:
        game_dict[final_parent_name][game_name] = {}

    # Update with names, then with any dupe entry
    game_dict[final_parent_name][game_name].update(game)
    game_dict[final_parent_name][game_name].update(dupe_entry)

    return game_dict


class GameFinder:

    def __init__(
        self,
        platform,
        dat=None,
        retool=None,
        ra_hashes=None,
        config_file=None,
        config=None,
        dupe_dict=None,
        platform_config=None,
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
            dupe_dict (dict, optional): Dupe dictionary. Defaults to None.
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
            log_dir = self.config.get("dirs", {}).get(
                "log_dir", os.path.join(os.getcwd(), "logs")
            )
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(
                log_level=log_level,
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

        self.dat = dat
        self.retool = retool
        self.ra_hashes = ra_hashes
        self.platform_config = platform_config

        # Info for dupes
        self.dupe_dict = dupe_dict
        self.dupe_dir = config.get("dirs", {}).get("dupe_dir", None)
        self.filter_dupes = config.get("gamefinder", {}).get("filter_dupes", True)

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(
        self,
        files,
    ):

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")
        self.logger.info(
            centred_string("Running GameFinder", total_length=self.log_line_length)
        )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        games_dict = self.get_game_dict(files)
        games_dict = dict(sorted(games_dict.items()))

        self.logger.info(
            centred_string(
                f"Found {len(games_dict)} games", total_length=self.log_line_length
            )
        )
        self.logger.debug(f"{'-' * self.log_line_length}")
        for gi, g in enumerate(games_dict):
            self.logger.debug(
                left_aligned_string(f"{g}:", total_length=self.log_line_length)
            )

            for ga in games_dict[g]:
                self.logger.debug(
                    left_aligned_string(
                        f"-> Priority {games_dict[g][ga]['priority']}: {ga}",
                        total_length=self.log_line_length,
                    )
                )

            if gi != len(games_dict) - 1:
                self.logger.debug(f"{'-' * self.log_line_length}")

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        return games_dict

    def get_game_dict(
        self,
        files,
    ):
        """Get a game dictionary out.

        From a list of files, parse out dupes, apply includes and excludes,
        and return a game dictionary.

        Args:
            files (dict): Dictionary of files with names for association
        """

        # We need to trim down dupes here. Otherwise, the
        # dict is just the list we already have
        game_dict = None
        if self.filter_dupes:
            game_dict = self.get_filter_dupes(files)

        # If the dupe filtering has failed, then just assign all the short names to the default dupe dict
        if game_dict is None:

            game_dict = {}

            for f in files:
                short_name = copy.deepcopy(files[f]["short_name"])
                game_dict[short_name] = {
                    short_name: DUPE_DEFAULT,
                }

        # Remove any excluded files
        if self.exclude_games is not None:
            games_to_remove = self.get_game_matches(
                game_dict,
                self.exclude_games,
            )
            if games_to_remove is not None:
                for g in games_to_remove:
                    del game_dict[g]

        # Include only included files
        if self.include_games is not None:

            games_to_include = self.get_game_matches(
                game_dict,
                self.include_games,
            )
            if games_to_include is not None:

                filtered_game_dict = {}
                for g in games_to_include:
                    filtered_game_dict[g] = game_dict[g]

                game_dict = copy.deepcopy(filtered_game_dict)
        return game_dict

    def get_game_matches(
        self,
        game_dict,
        games_to_match,
    ):
        """Get files that match an input dictionary (to properly handle dupes)

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
        game_dict_keys = [str(g) for g in game_dict_keys]

        if len(game_dict_keys) == 0:
            game_dict_keys = None

        return game_dict_keys

    def get_filter_dupes(self, games):
        """Parse down a list of files based on an input dupe list"""

        if self.dupe_dict is None and self.dupe_dir is None:
            raise ValueError(
                "dupe_dict or dupe_dir must be specified if filtering dupes"
            )

        if self.dupe_dict is None:
            dupe_file = os.path.join(self.dupe_dir, f"{self.platform} (dupes).json")
            if not os.path.exists(dupe_file):
                self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
                self.logger.warning(
                    centred_string(
                        "No dupe files found", total_length=self.log_line_length
                    )
                )
                self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
                return None
            self.dupe_dict = load_json(dupe_file)

        game_dict = {}

        # Loop over games, and the dupes dictionary. Also pull out various other important info
        for i, g in enumerate(games):

            # Look at the search terms
            game_dict = self.filter_by_search_terms(
                game=games[g],
                game_dict=game_dict,
            )

        return game_dict

    def filter_by_search_terms(
        self,
        game,
        game_dict=None,
    ):
        """Add entries to game dict based on search term conditions

        Will find possible parents, then add those to the game dict

        Args:
            game (dict): Dictionary containing various game names
            game_dict (dict): Dictionary of games to match against. Defaults
                to None, which will create an empty dict
        """

        if game_dict is None:
            game_dict = {}

        found_parents = self.get_parents(
            game_name=game,
        )

        for parent in found_parents:

            # If we have multiple matches, and it's not part of a compilation, freak out
            if len(found_parents) > 1:
                is_compilation = parent.get("dupe_entry").get("is_compilation", False)
                if not is_compilation:
                    self.logger.warning(
                        centred_string(
                            f"{game['original_name']} has multiple matches! "
                            f"This should not generally happen",
                            total_length=self.log_line_length,
                        )
                    )

            game_dict = add_dupe_entry_to_game_dict(
                game=game,
                game_dict=game_dict,
                parent=parent,
            )

        return game_dict

    def get_parents(
        self,
        game_name,
    ):
        """Get the parent(s) recursively searching through a dupe dict

        Because we can have compilations, find all cases where things match up

        Args:
            game_name (dict): game name to find parents for
        """

        # Keep track of the fact that we might have region-free names here
        if isinstance(game_name, dict):
            full_name = copy.deepcopy(game_name["full_name"])
            short_name = copy.deepcopy(game_name["short_name"])
            region_free_name = copy.deepcopy(game_name["region_free_name"])
        else:
            full_name = copy.deepcopy(game_name)
            short_name = copy.deepcopy(game_name)
            region_free_name = copy.deepcopy(game_name)

        # We do this by lowercase checking
        dupes = [{g: self.dupe_dict[g]} for g in self.dupe_dict]

        # Pull out all the clones (and whether they've got name types) so we can check that way as well
        all_clones = []
        name_types = []

        for d in self.dupe_dict:
            all_clones.append(
                {key: self.dupe_dict[d][key] for key in self.dupe_dict[d]}
            )

        for clone in all_clones:
            name_type = [clone[k].get("name_type", None) for k in clone]
            name_types.append(name_type)

        found_dupe = False

        found_parents = []

        # Check all the clones within the dupes. These can potentially
        # have different name types, so loop
        for clone, name_type, dupe in zip(all_clones, name_types, dupes):

            for c, n in zip(clone, name_type):

                found_dupe_in_clone = match_retool_search_terms(
                    full_name=full_name,
                    search_term=c,
                    short_name=short_name,
                    region_free_name=region_free_name,
                    match_type=n,
                )
                if found_dupe_in_clone:
                    found_dupe = True

                if found_dupe_in_clone:

                    parent_name = list(dupe.keys())[0]
                    dupe_entry = copy.deepcopy(clone[c])

                    # We need to apply filters here, hey
                    filters = clone[c].get("filters", None)
                    if filters is not None:

                        parent_name, dupe_entry = self.apply_filters(
                            parent_name=parent_name,
                            dupe_entry=dupe_entry,
                            game_name=game_name,
                            filters=filters,
                        )

                    # Set up the dictionary
                    found_parent = {
                        "parent_name": parent_name,
                        "dupe_name": c,
                        "dupe_entry": dupe_entry,
                    }

                    # Don't duplicate
                    if found_parent not in found_parents:
                        found_parents.append(found_parent)

        if not found_dupe:
            found_parents = copy.deepcopy(short_name)

        if found_parents is None:
            raise ValueError("Could not find a parent name!")

        if not isinstance(found_parents, list):
            found_parents = [found_parents]

        return found_parents

    def apply_filters(
        self,
        game_name,
        parent_name,
        dupe_entry,
        filters,
    ):
        """Apply filters to game if conditions are met

        Args:
            game_name: Dictionary containing various game names
            parent_name: Game name
            dupe_entry: Dictionary of game properties
            filters: Filters with conditions and results to apply
        """

        # Parse out the filename
        file_to_parse = {game_name["full_name"]: game_name}
        rp = ROMParser(
            platform=self.platform,
            game=parent_name,
            config=self.config,
            dat=self.dat,
            retool=self.retool,
            ra_hashes=self.ra_hashes,
            default_config=self.default_config,
            regex_config=self.regex_config,
            logger=self.logger,
        )
        rom_parsed = rp.run(file_to_parse)
        rom_parsed = rom_parsed.get(game_name["full_name"], None)

        if rom_parsed is None:
            raise ValueError("ROM parsing failed")

        # Having parsed the file, now loop over the conditions
        for filt in filters:

            conditions_met = []
            for c in filt["conditions"]:
                if c == "matchLanguages":
                    condition_met = check_languages(
                        filt["conditions"][c], rom_parsed["languages"]
                    )
                elif c == "matchRegions":
                    condition_met = check_regions(
                        filt["conditions"][c], rom_parsed["regions"]
                    )
                elif c == "matchString":
                    condition_met = check_string(
                        filt["conditions"][c], game_name["full_name"]
                    )
                elif c == "regionOrder":
                    condition_met = check_region_order(
                        filt["conditions"][c],
                        self.config["region_preferences"],
                        all_regions=list(self.default_config["regions"]),
                    )
                else:
                    raise ValueError(f"Unsure how to deal with condition {c}")
                conditions_met.append(condition_met)

            # If we've met the conditions, then apply the results
            if all(conditions_met):
                parent_name, dupe_entry = self.apply_results(
                    parent_name,
                    dupe_entry,
                    filt["results"],
                )

        return parent_name, dupe_entry

    def apply_results(
            self,
            parent_name,
            game_dict,
            results,
    ):
        """Apply results to a filtered match

        Args:
            parent_name: Parent name
            game_dict: Dictionary of game properties
            results: Dictionary of results to apply to the game/game dict
        """

        for r in results:

            # If we're changing the name, that gets pulled out here
            if r == "group":
                parent_name = copy.deepcopy(results[r])

            # If we're changing priority, edit the game dict
            elif r == "priority":
                game_dict[r] = results[r]

            # If the filter is for supersets, take that bool
            elif r == "superset":
                game_dict["flag_as_superset"] = results[r]

            # Ignore local names, since we won't use them
            elif r == "localNames":
                continue

            # If we have something else unexpected, raise a warning but do nothing
            else:
                self.logger.warning(f"Unsure how to deal with result type {r}")
                continue

        return parent_name, game_dict
