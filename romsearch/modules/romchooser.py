import copy
import os
from collections import Counter

import numpy as np
import packaging.version
from packaging import version

import romsearch
from ..util import (setup_logger,
                    create_bar,
                    load_yml,
                    )

BOOL_FILTERS = [
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


def argsort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)


def remove_rom_dict_entries(rom_dict,
                            key,
                            remove_type="bool",
                            bool_remove=True,
                            list_preferences=None,
                            ):
    """Remove entries from the game dict based on various rules"""

    f_to_delete = []
    for f in rom_dict:

        # Bool type, we can filter either on Trues or Falses
        if remove_type == "bool":

            key_val = rom_dict[f].get(key, None)
            if key_val is None:
                continue

            if bool_remove:
                if key_val:
                    f_to_delete.append(f)
            else:
                if not key_val:
                    f_to_delete.append(f)

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
                f_to_delete.append(f)

        else:
            raise ValueError("remove_type should be one of bool, list")

    f_to_delete = np.unique(f_to_delete)
    for f in f_to_delete:
        rom_dict.pop(f)

    return rom_dict


def get_best_version(rom_dict,
                     version_key="version",
                     ):
    """Pull out all the regions we've got left, to loop over and search for versions"""

    all_regions = np.unique([",".join(rom_dict[key]["regions"]) for key in rom_dict])

    for region in all_regions:
        region_rom_dict = {key: rom_dict[key][version_key]
                           for key in rom_dict if ",".join(rom_dict[key]["regions"]) == region}

        # Pull out all the versions we have
        all_vers = [region_rom_dict[key] for key in region_rom_dict]
        # If we have anything here that doesn't have a version, set it to v0
        all_vers = [vers if vers != "" else "v0" for vers in all_vers]

        # If we have lettered versions, convert these to numbers
        for i, vers in enumerate(all_vers):
            try:
                version.parse(vers)
            except packaging.version.InvalidVersion:
                all_vers[i] = f"v{ord(vers[1:])}"

        all_keys = [key for key in region_rom_dict]

        max_ver = max(all_vers, key=version.parse)
        max_ver_idx = np.where(np.asarray(all_vers) == max_ver)[0]

        max_ver_key = np.asarray(all_keys)[max_ver_idx]

        keys_to_pop = []
        for key in all_keys:
            if key not in max_ver_key:
                keys_to_pop.append(key)

        for key in keys_to_pop:
            rom_dict.pop(key)

    return rom_dict


def get_best_rom_per_region(rom_dict,
                            region_preferences,
                            ):
    """For each individual region, get an overall best ROM"""
    for reg_pref in region_preferences:

        roms = []

        for key in rom_dict:
            if reg_pref in rom_dict[key]["regions"]:
                roms.append(key)

        if len(roms) > 1:
            roms = get_best_roms(roms, rom_dict)

            keys_to_pop = []
            for f in rom_dict:
                if f not in roms and reg_pref in rom_dict[f]["regions"]:
                    keys_to_pop.append(f)

            for key in keys_to_pop:
                rom_dict.pop(key)

    return rom_dict

def remove_unwanted_roms(rom_dict, key_to_check, check_type="include"):
    """Remove unwanted ROMs from the dict

    If we have multiple versions lying around that may be preferred or demoted for some reason, parse them
    out here. Do this per region combo
    """

    all_regions = []
    for key in rom_dict:
        all_regions.extend(",".join(rom_dict[key]["regions"]))
    all_regions = np.unique(all_regions)

    keys_to_pop = []

    for region in all_regions:

        region_game_keys = [key for key in rom_dict if region in rom_dict[key]["regions"]]

        # Only filter things down if we've got multiples here
        if len(region_game_keys) > 1:
            found_demoted = [rom_dict[key][key_to_check] for key in region_game_keys]

            # Remove these, but only if we have some but not all
            if 0 < sum(found_demoted) < len(found_demoted):
                for key in region_game_keys:
                    if check_type == "include":
                        if not rom_dict[key][key_to_check]:
                            keys_to_pop.append(key)
                    elif check_type == "exclude":
                        if rom_dict[key][key_to_check]:
                            keys_to_pop.append(key)
                    else:
                        raise ValueError(f"check_type should be one of include or exclude")

    for key in keys_to_pop:
        rom_dict.pop(key)

    return rom_dict


def get_best_roms(files, rom_dict):
    """Get the best ROM(s) from a list, using a scoring system"""

    # Positive scores
    improved_version_score = 1
    version_score = 10
    revision_score = 100
    budget_edition_score = 1000

    # Negative scores
    demoted_version_score = -1
    alternate_version_score = -1
    modern_version_score = -10
    priority_score = -100

    file_scores = np.zeros(len(files))

    # Improved or demoted versions
    file_scores += improved_version_score * np.array([int(rom_dict[f]["improved_version"]) for f in files])
    file_scores += demoted_version_score * np.array([int(rom_dict[f]["demoted_version"]) for f in files])
    file_scores += budget_edition_score * np.array([int(rom_dict[f]["budget_edition"]) for f in files])
    file_scores += alternate_version_score * np.array([int(rom_dict[f]["alternate"]) for f in files])

    # Version numbering, which needs to be parsed
    file_scores += version_score * add_versioned_score(files, rom_dict, "version")
    file_scores += revision_score * add_versioned_score(files, rom_dict, "revision")

    # Downweight modern versions
    file_scores += modern_version_score * np.array([int(rom_dict[f]["modern_version"]) for f in files])

    # Priority scoring, where we subtract 1 so that the highest priority has no changed
    file_scores += priority_score * (np.array([int(rom_dict[f]["priority"]) for f in files]) - 1)

    files_idx = np.where(file_scores == np.nanmax(file_scores))[0]
    files = np.asarray(files)[files_idx]

    return files


def add_versioned_score(files, rom_dict, key):
    """Get an order for versioned strings"""

    # Ensure we have a version here. If blank, set to v0
    rom_dict = copy.deepcopy(rom_dict)
    for f in rom_dict:
        if rom_dict[f][key] == "":
            rom_dict[f][key] = "v0"

    versions = np.array([version.parse(rom_dict[f][key]) for f in files])
    versions_clean = [key for key, value in Counter(versions).most_common()]
    version_vals = sorted(range(len(versions_clean)), key=versions.__getitem__)

    file_scores_version = np.zeros(len(files))
    for v_idx, v in enumerate(versions_clean):
        for f_idx, f in enumerate(files):
            if version.parse(rom_dict[f][key]) == v:
                file_scores_version[f_idx] += version_vals[v_idx]

    return file_scores_version


def filter_by_list(rom_dict,
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
            if key_pref in rom_dict[val][key]:
                roms.append(val)
                found_key = True

    # If we have multiple matches here, define a best match using scoring system
    if len(roms) > 1:
        roms = get_best_roms(roms,
                             rom_dict,
                             )

    keys_to_pop = []
    for f in rom_dict:
        if f not in roms:
            keys_to_pop.append(f)

    for key in keys_to_pop:
        rom_dict.pop(key)

    return rom_dict


class ROMChooser:

    def __init__(self,
                 config_file,
                 platform,
                 game
                 ):
        """ROM choose tool

        This works per-game, per-platform, so must be specified here
        """

        if platform is None:
            raise ValueError("platform must be specified")
        self.platform = platform

        logger_add_dir = str(os.path.join(platform, game))

        self.logger = setup_logger(log_level="info",
                                   script_name=f"ROMChooser",
                                   additional_dir=logger_add_dir,
                                   )

        config = load_yml(config_file)

        mod_dir = os.path.dirname(romsearch.__file__)

        default_config_file = os.path.join(mod_dir, "configs", "defaults.yml")
        self.default_config = load_yml(default_config_file)

        platform_config_file = os.path.join(mod_dir, "configs", "platforms", f"{platform}.yml")
        self.platform_config = load_yml(platform_config_file)

        # Region preference (usually set USA for retroachievements, can also be a list to fall back to)
        region_preferences = config.get("region_preferences", self.default_config["default_region"])
        if isinstance(region_preferences, str):
            region_preferences = [region_preferences]

        for region_pref in region_preferences:
            if region_pref not in self.default_config["regions"]:
                raise ValueError(f"Regions should be any of {self.default_config['regions']}, not {region_pref}")

        self.region_preferences = region_preferences

        # Language preference (usually set En, can also be a list to fall back to)
        language_preferences = config.get("language_preferences", self.default_config["default_language"])
        if isinstance(language_preferences, str):
            language_preferences = [language_preferences]

        for language_pref in language_preferences:
            if language_pref not in self.default_config["languages"]:
                raise ValueError(f"Regions should be any of {self.default_config['languages']}, not {language_pref}")

        self.language_preferences = language_preferences

        # Various filters. First are the boolean ones
        bool_filters = config.get("romchooser", {}).get("bool_filters", "all_but_games")
        if "all" in bool_filters:
            all_bool_filters = copy.deepcopy(BOOL_FILTERS)
            if "all_but" in bool_filters:
                filter_to_remove = bool_filters.split("all_but_")[-1]
                all_bool_filters.remove(filter_to_remove)
            bool_filters = copy.deepcopy(all_bool_filters)

        if isinstance(bool_filters, str):
            all_bool_filters = [bool_filters]
        else:
            all_bool_filters = bool_filters
        self.bool_filters = all_bool_filters

        self.filter_regions = config.get("romchooser", {}).get("filter_regions", True)
        self.filter_languages = config.get("romchooser", {}).get("filter_languages", True)
        self.allow_multiple_regions = config.get("romchooser", {}).get("allow_multiple_regions", False)
        self.use_best_version = config.get("romchooser", {}).get("use_best_version", True)

        self.dry_run = config.get("romchooser", {}).get("dry_run", False)

    def run(self,
            rom_dict):
        """Run the ROM chooser"""

        self.logger.info(create_bar(f"START ROMChooser"))

        rom_dict = self.run_chooser(rom_dict)

        self.logger.info(create_bar(f"FINISH ROMChooser"))

        return rom_dict

    def run_chooser(self,
                    rom_dict):
        """Make a ROM choice based on various factors

        This chooser works in this order:

        - Removing any demo files
        - Removing any beta files
        - Removing anything where the language isn't in the user preferences
            (for files with no language info, this will skipped)
        - Removing anything where the region isn't in the user preferences
        - Get some "best version", via:
            - Revision number
            - Version number
            - Some kind of special name to indicate an improved version
        - Finally, if we only allow one region, parse down to a single region (first in the list)
        """

        for f in self.bool_filters:
            self.logger.debug(f"Filtering {f}")
            if f in BOOL_FILTERS:
                rom_dict = remove_rom_dict_entries(rom_dict,
                                                   f,
                                                   remove_type="bool",
                                                   bool_remove=True,
                                                   )
            else:
                raise ValueError(f"Unknown filter type {f}")

        # Language
        if self.filter_languages:
            self.logger.debug("Filtering languages")
            rom_dict = remove_rom_dict_entries(rom_dict,
                                               "languages",
                                               remove_type="list",
                                               list_preferences=self.language_preferences,
                                               )

        # Regions
        if self.filter_regions:
            self.logger.debug("Filtering regions")
            rom_dict = remove_rom_dict_entries(rom_dict,
                                               "regions",
                                               remove_type="list",
                                               list_preferences=self.region_preferences,
                                               )

        # Remove versions we potentially don't want around
        if self.use_best_version:
            self.logger.debug("Getting best version")
            rom_dict = get_best_version(rom_dict)
            rom_dict = remove_unwanted_roms(rom_dict, key_to_check="improved_versions", check_type="include")
            rom_dict = remove_unwanted_roms(rom_dict, key_to_check="budget_edition", check_type="include")
            rom_dict = remove_unwanted_roms(rom_dict, key_to_check="demoted_versions", check_type="exclude")
            rom_dict = remove_unwanted_roms(rom_dict, key_to_check="modern_versions", check_type="exclude")
            rom_dict = remove_unwanted_roms(rom_dict, key_to_check="alternate", check_type="exclude")
            rom_dict = get_best_rom_per_region(rom_dict,
                                               self.region_preferences,
                                               )

        if not self.allow_multiple_regions:
            self.logger.debug("Trimming down to a single region")
            rom_dict = filter_by_list(rom_dict,
                                      "regions",
                                      self.region_preferences,
                                      )

        return rom_dict
