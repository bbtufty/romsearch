from collections import Counter

import copy
import numpy as np
import os
from packaging import version

import romsearch
from ..util import (
    setup_logger,
    centred_string,
    left_aligned_string,
    load_yml,
)

DAT_FILTERS = [
    "add-ons",
    "applications",
    "audio",
    "bad_dumps",
    "console",
    "bonus_discs",
    "coverdiscs",
    "demos",
    "educational",
    "games",
    "manuals",
    "multimedia",
    "pirate",
    "preproduction",
    "promotional",
    "unlicensed",
    "video",
]


def get_sanitized_version(ver):
    """Get a sanitized version for potentially weird versioning

    Args:
        ver: version to sanitize
    """

    # If we don't have a version, assume v0
    if ver.lower() in [""]:
        ver = "v0"

    # If we just have "rev", assume a v1
    if ver.lower() in ["rev"]:
        ver = "v1"

    # If we have lettered versions, convert these to numbers
    if ver[1:].isalpha():
        ver = f"v{ord(ver[1:])}"

    # If we have a v.something, replace that here so versions can be parsed
    if ver[:2] == "v.":
        ver = f"v{ver[2:]}"

    # If we have a letter at the end, replace with an ordinal
    if ver[-1].isalpha():
        ver = f"{ver[:-1]}.{ord(ver[-1])}"

    return ver


def argsort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)


def remove_rom_dict_entries(
    rom_dict,
    key,
    remove_type="bool",
    bool_remove=True,
    list_preferences=None,
):
    """Exclude entries from the game dict based on various rules"""

    f_to_exclude = []
    for f in rom_dict:

        # Bool type, we can filter either on Trues or Falses
        if remove_type == "bool":

            key_val = rom_dict[f].get(key, None)
            if key_val is None:
                continue

            if bool_remove:
                if key_val:
                    f_to_exclude.append(f)
            else:
                if not key_val:
                    f_to_exclude.append(f)

        elif remove_type == "list":

            if list_preferences is None:
                raise ValueError("list_preferences not specified")

            # If there's no information in there, assume we're OK
            if len(rom_dict[f][key]) == 0:
                continue

            found = False
            for val in rom_dict[f][key]:
                if val in list_preferences:
                    found = True
            if not found:
                f_to_exclude.append(f)

        else:
            raise ValueError("remove_type should be one of bool, list")

    f_to_exclude = np.unique(f_to_exclude)
    f_to_exclude = [str(f) for f in f_to_exclude]
    for f in f_to_exclude:
        rom_dict[f]["excluded"] = True
        rom_dict[f]["excluded_reason"].append(key)

    return rom_dict


def add_versioned_score(files, rom_dict, key):
    """Get an order for versioned strings"""

    # Ensure we have a version here. If blank, set to v0
    rom_dict = copy.deepcopy(rom_dict)
    for f in rom_dict:
        rom_dict[f][key] = get_sanitized_version(rom_dict[f][key])

    versions = [version.parse(rom_dict[f][key]) for f in files]
    versions_sorted = np.unique(sorted(versions))

    file_scores_version = np.zeros(len(files))
    for i, v in enumerate(versions_sorted):
        v_idx = np.where(np.asarray(versions) == v)[0]
        file_scores_version[v_idx] += i

    return file_scores_version


def add_ordered_score(files, rom_dict, priorities, score_key):
    """Add an ordered score, include the priority of the order

    Args:
        files (list): List of files to score
        rom_dict (dict): Dictionary of ROMs
        priorities (list): List of values in priority order
        score_key (str): Corresponding score key for the priorities in the rom_dict
    """

    score_dict = {}

    # Go backwards so the first entry is the highest priority
    for i, prio in enumerate(priorities[::-1]):
        score_dict[prio] = i + 1

    scores = np.zeros_like(files, dtype=int)
    for i, f in enumerate(files):
        for key in rom_dict[f][score_key]:
            if key in score_dict:
                scores[i] += score_dict[key]

    return scores


def filter_by_list(
    rom_dict,
    key,
    key_prefs,
):
    """Find file with highest value in given list. If there are multiple matches, find the most updated one"""

    roms = []

    found_key = False
    for key_pref in key_prefs:

        if found_key:
            continue

        for val in rom_dict:

            # Only count this as "found" if we haven't already excluded
            if key_pref in rom_dict[val][key] and not rom_dict[val]["excluded"]:
                roms.append(val)
                found_key = True

    keys_to_exclude = []
    for f in rom_dict:
        if f not in roms:
            keys_to_exclude.append(f)

    for e in keys_to_exclude:

        # Only exclude by preference if we haven't already excluded absolutely
        if key not in rom_dict[e]["excluded_reason"]:
            rom_dict[e]["excluded"] = True
            rom_dict[e]["excluded_reason"].append(f"{key}_preference")

    return rom_dict


def filter_compilations(
    rom_dict,
):
    """Filter out compilations if we have them

    Args:
        rom_dict (dict): Dictionary of ROMs
    """

    compilations = []
    non_compilations = []

    for r in rom_dict:
        if not rom_dict[r]["excluded"]:
            if rom_dict[r].get("is_compilation", False):
                compilations.append(r)
            else:
                non_compilations.append(r)

    # Only remove compilations if we have singular titles
    if len(non_compilations) > 0:
        for comp in compilations:
            rom_dict[comp]["excluded"] = True
            rom_dict[comp]["excluded_reason"].append("is_compilation")

    return rom_dict


class ROMChooser:

    def __init__(
        self,
        platform,
        game,
        config_file=None,
        config=None,
        default_config=None,
        regex_config=None,
        logger=None,
        log_line_sep="=",
        log_line_length=100,
    ):
        """ROM choose tool

        This works per-game, per-platform, so must be specified here

        Args:
            platform (str): Platform name
            game (str): Game name
            config_file (str, optional): Path to config file. Defaults to None.
            config (dict, optional): Configuration dictionary. Defaults to None.
            default_config (dict, optional): Default configuration dictionary. Defaults to None.
            regex_config (dict, optional): Configuration dictionary. Defaults to None.
            logger (logging.Logger, optional): Logger instance. Defaults to None.
            log_line_length (int, optional): Line length of log. Defaults to 100
        """

        if platform is None:
            raise ValueError("platform must be specified")
        self.platform = platform

        if game is None:
            raise ValueError("game must be specified")
        self.game = game

        if config_file is None and config is None:
            raise ValueError("config_file or config must be specified")

        if config is None:
            config = load_yml(config_file)
        self.config = config

        if logger is None:
            log_dir = self.config.get("dirs", {}).get(
                "log_dir", os.path.join(os.getcwd(), "logs")
            )
            logger_add_dir = str(os.path.join(platform, game))
            log_level = self.config.get("logger", {}).get("level", "info")
            logger = setup_logger(
                log_level=log_level,
                script_name=f"ROMChooser",
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

        # Region preference (usually set USA for retroachievements, can also be a list to fall back to)
        region_preferences = self.config.get(
            "region_preferences", self.default_config["default_region"]
        )
        if isinstance(region_preferences, str):
            region_preferences = [region_preferences]

        for region_pref in region_preferences:
            if region_pref not in self.default_config["regions"]:
                raise ValueError(
                    f"Regions should be any of {self.default_config['regions']}, not {region_pref}"
                )

        self.region_preferences = region_preferences

        # Language preference (usually set En, can also be a list to fall back to)
        language_preferences = self.config.get(
            "language_preferences", self.default_config["default_language"]
        )
        if isinstance(language_preferences, str):
            language_preferences = [language_preferences]

        for language_pref in language_preferences:
            if language_pref not in self.default_config["languages"]:
                raise ValueError(
                    f"Regions should be any of {self.default_config['languages']}, not {language_pref}"
                )

        self.language_preferences = language_preferences

        # Various filters. First are the boolean ones
        dat_filters = self.config.get("romchooser", {}).get(
            "dat_filters", "all_but_games"
        )
        if "all" in dat_filters:
            all_dat_filters = copy.deepcopy(DAT_FILTERS)
            if "all_but" in dat_filters:
                filter_to_remove = dat_filters.split("all_but_")[-1]
                all_dat_filters.remove(filter_to_remove)
            dat_filters = copy.deepcopy(all_dat_filters)

        if isinstance(dat_filters, str):
            dat_filters = [dat_filters]
        self.dat_filters = dat_filters

        self.filter_regions = self.config.get("romchooser", {}).get(
            "filter_regions", True
        )
        self.filter_languages = self.config.get("romchooser", {}).get(
            "filter_languages", True
        )
        self.use_best_version = self.config.get("romchooser", {}).get(
            "use_best_version", True
        )

        self.dry_run = self.config.get("romchooser", {}).get("dry_run", False)

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(self, rom_dict):
        """Run the ROM chooser"""

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")
        self.logger.info(
            centred_string(
                f"Running ROMChooser for {self.game}", total_length=self.log_line_length
            )
        )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        rom_dict = self.run_chooser(rom_dict)

        self.print_summary(rom_dict)

        # Filter out excluded ROMs before we return
        rom_dict = {
            key: rom_dict[key] for key in rom_dict if not rom_dict[key]["excluded"]
        }

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        return rom_dict

    def run_chooser(self, rom_dict):
        """Make a ROM choice based on various factors

        This chooser works in this order:

        * Filter out dat categories we don't want (e.g. demos, betas)
        * Filter out ROMs that don't have any languages in the user preferences
        * Filter out ROMs that don't have any regions in the user preferences

        For the ROMs left, we then choose a best one, using a scoring system with
        this priority:

        * Achievements
        * Regions
        * Languages
        * Budget editions
        * Versions and revisions
        * Improved versions

        We also demote ROMs, with this priority (most to least demoted):

        * Retool priority
        * Modern versions
        * Alternate versions
        * Demoted versions

        Args:
            rom_dict (dict): Dictionary of ROMs to choose between
        """

        # Add in whether these are excluded or not, and why
        for r in rom_dict:
            rom_dict[r]["excluded"] = False
            rom_dict[r]["excluded_reason"] = []

        for f in self.dat_filters:
            self.logger.debug(
                left_aligned_string(f"Filtering {f}", total_length=self.log_line_length)
            )
            if f in DAT_FILTERS:
                rom_dict = remove_rom_dict_entries(
                    rom_dict,
                    f,
                    remove_type="bool",
                    bool_remove=True,
                )
            else:
                raise ValueError(f"Unknown filter type {f}")

        # Language
        if self.filter_languages:
            self.logger.debug(
                left_aligned_string(
                    f"Filtering languages", total_length=self.log_line_length
                )
            )
            rom_dict = remove_rom_dict_entries(
                rom_dict,
                "languages",
                remove_type="list",
                list_preferences=self.language_preferences,
            )

        # Regions
        if self.filter_regions:
            self.logger.debug(
                left_aligned_string(
                    f"Filtering regions", total_length=self.log_line_length
                )
            )
            rom_dict = remove_rom_dict_entries(
                rom_dict,
                "regions",
                remove_type="list",
                list_preferences=self.region_preferences,
            )

        # If we have a split between singular titles and compilations, sort that out here
        self.logger.debug(
            left_aligned_string(
                f"Potentially filtering compilations", total_length=self.log_line_length
            )
        )
        rom_dict = filter_compilations(
            rom_dict,
        )

        # Remove versions we potentially don't want around
        if self.use_best_version:
            self.logger.debug(
                left_aligned_string(
                    f"Getting best version", total_length=self.log_line_length
                )
            )
            rom_dict = self.get_best_rom(
                rom_dict,
            )

        return rom_dict

    def print_summary(
        self,
        rom_dict,
    ):
        """Log out a nice summary of what ROM has been chosen here

        Args:
            rom_dict (dict): the ROM dictionary to summarize
        """

        if len(rom_dict) == 0:
            # Just say nothing found
            self.logger.info(
                centred_string("No ROMs found", total_length=self.log_line_length)
            )
        else:

            # Start with found ROMs, then excluded ROMs and reasons
            if np.sum([not rom_dict[r]["excluded"] for r in rom_dict]) > 0:
                self.logger.info(
                    centred_string("Included ROMs:", total_length=self.log_line_length)
                )

            for r in rom_dict:

                # Don't include the excluded ones here
                if rom_dict[r]["excluded"]:
                    continue

                self.logger.info(
                    left_aligned_string(f"-> {r}", total_length=self.log_line_length)
                )
                if rom_dict[r]["has_cheevos"]:
                    self.logger.info(
                        left_aligned_string(
                            f"--> Has RetroAchievements",
                            total_length=self.log_line_length,
                        )
                    )
                if rom_dict[r]["patch_file"] != "":
                    self.logger.info(
                        left_aligned_string(
                            f"--> Patch URL: {rom_dict[r]['patch_file']}",
                            total_length=self.log_line_length,
                        )
                    )

            if (
                np.sum([rom_dict[r]["excluded"] for r in rom_dict]) > 0
                and np.sum([not rom_dict[r]["excluded"] for r in rom_dict]) > 0
            ):
                self.logger.info(f"{'-' * self.log_line_length}")

            if np.sum([rom_dict[r]["excluded"] for r in rom_dict]) > 0:
                self.logger.info(
                    centred_string("Excluded ROMs:", total_length=self.log_line_length)
                )

            for r in rom_dict:

                # Don't include the excluded ones here
                if not rom_dict[r]["excluded"]:
                    continue

                # Make the exclusion reason more human-readable
                exclusion_reason = rom_dict[r]["excluded_reason"]
                exclusion_reason = [
                    e.capitalize().replace("_", " ") for e in exclusion_reason
                ]

                self.logger.info(
                    left_aligned_string(f"-> {r}", total_length=self.log_line_length)
                )
                self.logger.info(
                    left_aligned_string(
                        f"--> Reason(s): {', '.join(exclusion_reason)}",
                        total_length=self.log_line_length,
                    )
                )

        return True

    def get_best_roms(
        self,
        files,
        rom_dict,
    ):
        """Get the best ROM(s) from a list, using a scoring system"""

        # Positive scores
        improved_version_score = 1e2
        version_score = 1e4
        revision_score = 1e6
        budget_edition_score = 1e8
        language_score = 1e10
        region_score = 1e12
        superset_score = 1e14
        cheevo_score = 1e16

        # Negative scores
        compilation_score = -1
        demoted_version_score = -1e2
        alternate_version_score = -1e2
        modern_version_score = -1e4
        priority_score = -1e6

        file_scores = np.zeros(len(files))

        # Just stepping through the scores in order.

        # Positive scores

        # Improved version
        file_scores += improved_version_score * np.array(
            [int(rom_dict[f]["improved_version"]) for f in files]
        )

        # Version numbering, which needs to be parsed. We edit these to only add a little each time
        version_score_to_add = add_versioned_score(files, rom_dict, "version")
        file_scores += version_score * (1 + (version_score_to_add - 1) / 100)

        # Revision numbering, again parsed
        revision_score_to_add = add_versioned_score(files, rom_dict, "revision")
        file_scores += revision_score * (1 + (revision_score_to_add - 1) / 100)

        # Budget edition
        file_scores += budget_edition_score * np.array(
            [int(rom_dict[f]["budget_edition"]) for f in files]
        )

        # Language priorities
        language_score_to_add = add_ordered_score(
            files, rom_dict, priorities=self.language_preferences, score_key="languages"
        )
        file_scores += language_score * (1 + (language_score_to_add - 1) / 100)

        # Regions priorities
        region_score_to_add = add_ordered_score(
            files,
            rom_dict,
            priorities=self.region_preferences,
            score_key="regions",
        )
        file_scores += region_score * (1 + (region_score_to_add - 1) / 100)

        # Superset score
        file_scores += superset_score * np.array(
            [rom_dict[f].get("is_superset", False) for f in files]
        )

        # Achievement hashes
        file_scores += cheevo_score * np.array(
            [int(rom_dict[f]["has_cheevos"]) for f in files]
        )

        # Negative scores

        # Compilation score
        file_scores += compilation_score * np.array(
            [rom_dict[f].get("is_compilation", False) for f in files]
        )

        # Demoted version
        file_scores += demoted_version_score * np.array(
            [int(rom_dict[f]["demoted_version"]) for f in files]
        )

        # Alternate version
        file_scores += alternate_version_score * np.array(
            [int(rom_dict[f]["alternate"]) for f in files]
        )

        # Modern version
        file_scores += modern_version_score * np.array(
            [int(rom_dict[f]["modern_version"]) for f in files]
        )

        # Priority scoring. We subtract 1 so that the highest priority has no change
        file_scores += priority_score * (
            np.array([int(rom_dict[f]["priority"]) for f in files]) - 1
        )

        files_idx = np.where(file_scores == np.nanmax(file_scores))[0]
        files = np.asarray(files)[files_idx]

        return files

    def get_best_rom(
        self,
        rom_dict,
    ):
        """Get an overall best ROM using a scoring system"""

        roms = []

        for key in rom_dict:
            if not rom_dict[key]["excluded"]:
                roms.append(key)

        if len(roms) > 1:
            roms = self.get_best_roms(roms, rom_dict)

            keys_to_exclude = []
            for f in rom_dict:
                if f not in roms:
                    keys_to_exclude.append(f)

            for key in keys_to_exclude:
                # Only exclude here if there isn't already another reason
                if len(rom_dict[key]["excluded_reason"]) == 0:
                    rom_dict[key]["excluded"] = True
                    rom_dict[key]["excluded_reason"].append(f"not_highest_score")

        return rom_dict
