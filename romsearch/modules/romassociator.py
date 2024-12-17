import copy
import os
import re
from iso639 import Lang

import romsearch
from .romparser import ROMParser
from ..util import (
    setup_logger,
    load_yml,
    centred_string,
)


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


def apply_results(
    game,
    game_dict,
    results,
):
    """Apply results to a filtered match

    Args:
        game: Game name
        game_dict: Dictionary of game properties
        results: Dictionary of results to apply to the game/game dict
    """

    for r in results:

        # If we're changing the name, that gets pulled out here
        if r == "group":
            game = copy.deepcopy(results[r])

        # If we're changing priority, edit the game dict
        elif r == "priority":
            game_dict[r] = results[r]

        # Ignore local names, since we won't use them
        elif r == "localNames":
            continue

        else:
            print(game, game_dict)
            raise ValueError(f"Unsure how to deal with result type {r}")

    return game, game_dict


class ROMAssociator:

    def __init__(
        self,
        platform=None,
        dat=None,
        retool=None,
        ra_hashes=None,
        config_file=None,
        config=None,
        platform_config=None,
        regex_config=None,
        default_config=None,
        logger=None,
        log_line_sep="=",
        log_line_length=100,
    ):
        """Tool for associating ROMs to games

        This will primarily use a list of associations, although there are also more granular
        options for filtering based on specific retool conditions

        Args:
            platform (str, optional): Platform name. Defaults to None, which will throw a ValueError.
            dat (dict): Parsed dat dictionary. Defaults to None, which will try to load the dat file if it exists
            retool (dict): Retool dictionary. Defaults to None, which will try to load the file if it exists
            ra_hashes (dict): RA hash dictionary. Defaults to None, which will try to load the file if it exists
            config_file (str, optional): path to config file. Defaults to None.
            config (dict, optional): configuration dictionary. Defaults to None.
            platform_config (dict, optional): platform configuration dictionary. Defaults to None.
            regex_config (dict, optional): regex configuration dictionary. Defaults to None.
            default_config (dict, optional): default configuration dictionary. Defaults to None.
            logger (logging.Logger, optional): logger instance. Defaults to None.
            log_line_length (int, optional): Line length of log. Defaults to 100
        """

        if config_file is None and config is None:
            raise ValueError("config_file or config must be specified")

        if config is None:
            config = load_yml(config_file)
        self.config = config

        self.platform = platform

        # Pull in platform config that we need
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

        if logger is None:
            log_dir = self.config.get("dirs", {}).get(
                "log_dir", os.path.join(os.getcwd(), "logs")
            )
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(
                log_level=log_level,
                script_name=f"ROMAssociator",
                log_dir=log_dir,
                additional_dir=platform,
            )
        self.logger = logger

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(
        self,
        files,
        games,
    ):
        """Run the ROM associator"""

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")
        self.logger.info(
            centred_string("Running ROMAssociator", total_length=self.log_line_length)
        )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        associations = self.run_associator(files, games)

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        return associations

    def run_associator(self, files, games):
        """Associate files with games

        Args:
            files: List of files to associate
            games: List of games to associate
        """

        self.logger.info(
            centred_string(
                f"Associating {len(files)} files to {len(games)} games",
                total_length=self.log_line_length,
            )
        )

        associations = {}

        # Loop over each file
        for f in files:

            # Loop over each game
            for game in games:

                # We check by a lowercase version of the short name
                f_lower = files[f]["short_name"].lower()
                for g in games[game]:

                    g_lower = g.lower()

                    if f_lower == g_lower:

                        # Pull out the particular dictionary and a copy
                        # of the game name. We'll need these separately
                        # as they may get updated by filters
                        final_game = copy.deepcopy(game)
                        final_game_dict = copy.deepcopy(games[game][g])

                        # Pull out potential filters
                        filters = games[game][g].get("filters", None)
                        if filters is not None:
                            final_game, final_game_dict = self.apply_filters(
                                game=final_game,
                                game_dict=final_game_dict,
                                file=f,
                                file_dict=files[f],
                                filters=filters,
                            )

                        # Make sure we match by lower case, just to be sure
                        all_associations = [k for k in associations]
                        all_associations_lower = [k.lower() for k in all_associations]

                        if final_game.lower() not in all_associations_lower:
                            associations[final_game] = {}
                        else:
                            idx = all_associations.index(final_game)
                            final_game = all_associations[idx]

                        # Update the dictionary as appropriate
                        if f not in associations[final_game]:
                            associations[final_game][f] = {}
                        associations[final_game][f].update(final_game_dict)

                        # If we're duplicating a match, and it's not part of a compilation, freak out
                        is_compilation = final_game_dict.get("is_compilation", False)
                        if files[f]["matched"] and not is_compilation:
                            self.logger.warning(
                                centred_string(
                                    f"{f} has already been matched! "
                                    f"This should not generally happen",
                                    total_length=self.log_line_length,
                                )
                            )

                        files[f]["matched"] = True

        # Log out any unmatched files
        self.log_unmatched_files(files)

        return associations

    def apply_filters(
        self,
        file,
        file_dict,
        game,
        game_dict,
        filters,
    ):
        """Apply filters to game if conditions are met

        Args:
            file: Filename for ROM
            file_dict: Dictionary of file properties
            game: Game name
            game_dict: Dictionary of game properties
            filters: Filters with conditions and results to apply
        """

        # Parse out the filename
        file_to_parse = {file: file_dict}
        rp = ROMParser(
            platform=self.platform,
            game=game,
            config=self.config,
            dat=self.dat,
            retool=self.retool,
            ra_hashes=self.ra_hashes,
            default_config=self.default_config,
            regex_config=self.regex_config,
            logger=self.logger,
        )
        rom_parsed = rp.run(file_to_parse)
        rom_parsed = rom_parsed.get(file, None)

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
                    condition_met = check_string(filt["conditions"][c], file)
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
                game, game_dict = apply_results(
                    game,
                    game_dict,
                    filt["results"],
                )

        return game, game_dict

    def log_unmatched_files(self, files):
        """Log out files we haven't matched

        Args:
            files: Dictionary of files with a flag for whether they've
                been matched
        """

        unmatched = [f for f in files if not files[f]["matched"]]
        n_unmatched = len(unmatched)

        if n_unmatched > 0:
            self.logger.warning(
                centred_string(
                    f"Failed to associate {n_unmatched} files",
                    total_length=self.log_line_length,
                )
            )
        else:
            self.logger.info(
                centred_string(
                    f"All files associated", total_length=self.log_line_length
                )
            )

        self.logger.debug(f"{'-' * self.log_line_length}")
        self.logger.debug(
            centred_string("Unmatched files:", total_length=self.log_line_length)
        )
        self.logger.debug(f"{'-' * self.log_line_length}")
        for f in unmatched:
            self.logger.debug(centred_string(f"{f}", total_length=self.log_line_length))
        self.logger.debug(f"{'-' * self.log_line_length}")
