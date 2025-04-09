import copy
import os

from ..util import (
    load_yml,
    save_yml,
    load_json,
    save_json,
    setup_logger,
    get_dat,
    format_dat,
    centred_string,
)

PLAYLIST_EXTS = tuple(
    [
        ".cue",
    ]
)


def get_checksums(
    dat,
    sort=False,
):
    """Get checksums out of a parsed DAT file

    Args:
        dat: Parsed DAT file
        sort: Whether to sort the dictionary. Defaults to False.
    """

    dat_checksums = {}
    for d in dat:

        dat_checksums[d] = {}

        # Get list of ROM files out
        d_roms = dat[d]["rom"]
        if isinstance(d_roms, dict):
            d_roms = [d_roms]

        # Record number of files
        dat_checksums[d]["n_files"] = len(d_roms)

        # Get out MD5 checksums
        d_md5s = [
            d_rom["md5"].lower()
            for d_rom in d_roms
            if not d_rom["name"].endswith(PLAYLIST_EXTS)
        ]
        d_md5s.sort()

        # Record checksums
        dat_checksums[d]["md5"] = copy.deepcopy(d_md5s)

    if sort:
        dat_checksums = dict(sorted(dat_checksums.items()))

    return dat_checksums


class DATMapper:

    def __init__(
        self,
        platform=None,
        config_file=None,
        config=None,
        logger=None,
        log_line_sep="=",
        log_line_length=100,
    ):
        """Map names in dats from old dat to new dat

        Will take a dat file, and a platform-matching dat file in some mapping folder,
        and search through MD5 checksums to find matches

        Args:
            platform (str, optional): Platform name. Defaults to None, which will throw a ValueError
            config_file (str, optional): Configuration file. Defaults to None
            config (dict, optional): Configuration dictionary. Defaults to None
            logger (logging.Logger, optional): Logger instance. Defaults to None
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
                script_name=f"DATParser",
                log_dir=log_dir,
                additional_dir=platform,
            )
        self.logger = logger
        self.mapped_dat_dir = self.config.get("dirs", {}).get("mapped_dat_dir", None)

        if self.mapped_dat_dir is None:
            raise ValueError("mapped_dat_dir must be specified in config")

        self.platform = platform

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(
        self,
        dat,
    ):
        """Run the DATMapper, using an input dat

        Args:
            dat: Parsed dat dictionary
        """

        dat_mappings = None

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")
        self.logger.info(
            centred_string("Running DATMapper", total_length=self.log_line_length)
        )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        old_dat = self.get_old_dat()

        if old_dat is not None:

            dat_mappings = self.compare_dats(
                dat=dat,
                old_dat=old_dat,
            )

            self.logger.info(f"{'-' * self.log_line_length}")

            self.logger.info(
                centred_string(
                    f"Found {len(dat_mappings)} changed names between dat files",
                    total_length=self.log_line_length,
                )
            )

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        return dat_mappings

    def get_old_dat(self):
        """Get the old dat from the mapped DAT dir"""

        old_dat = None
        found_old_dat = False

        # Start by seeing if we have a parsed JSON already
        old_dat_name_json = os.path.join(self.mapped_dat_dir, f"{self.platform}.json")
        if os.path.exists(old_dat_name_json):
            old_dat = load_json(old_dat_name_json)
            found_old_dat = True

        # If we don't have a JSON, load in the dat and parse out
        if not found_old_dat:
            old_dat_name = os.path.join(self.mapped_dat_dir, f"{self.platform}.dat")
            if not os.path.exists(old_dat_name):
                self.logger.warning(
                    centred_string(
                        f"dat file {old_dat_name} not found",
                        total_length=self.log_line_length,
                    )
                )
                return None
            old_dat = get_dat(old_dat_name)
            old_dat = format_dat(old_dat)
            save_json(old_dat, old_dat_name_json)

        return old_dat

    def compare_dats(
        self,
        dat,
        old_dat,
    ):
        """Compare dats, producing a dictionary of mappings between them

        Args:
            dat: New dat to compare to
            old_dat: Old dat to compare against
        """

        out_file = os.path.join(self.mapped_dat_dir, f"{self.platform}.yml")

        dat_mappings = {}

        # Pull out a) the number of files and b) a list of checksums for each
        # individual ROM file for the two dats. Sort them so we can hunt through
        # more quickly
        dat_checksums = get_checksums(
            dat,
            sort=True,
        )
        old_dat_checksums = get_checksums(
            old_dat,
            sort=True,
        )

        # Keep track of ones we've matched for speed, since they should be unique
        d_found = [False] * len(dat)
        od_found = [False] * len(old_dat)

        od_keys = list(old_dat.keys())

        # First, just search for exact matches
        for idx_d, d in enumerate(dat):

            od_checksums = old_dat_checksums.get(d, {}).get("md5", None)
            if od_checksums is None:
                continue

            # If we have a match, mark as found. Names match,
            # so we don't need to map
            if dat_checksums[d]["md5"] == od_checksums:

                idx_od = od_keys.index(d)

                d_found[idx_d] = True
                od_found[idx_od] = True

        for idx_d, d in enumerate(dat):

            # If we've already matched, move on
            if d_found[idx_d]:
                continue

            for idx_od, od in enumerate(old_dat):

                # If we've already matched, move on
                if d_found[idx_d]:
                    continue
                if od_found[idx_od]:
                    continue

                # If we don't have the same number of files, skip
                if dat_checksums[d]["n_files"] != old_dat_checksums[od]["n_files"]:
                    continue

                # Check if names match
                names_match = d == od

                # If we have a match, mark as found
                if dat_checksums[d]["md5"] == old_dat_checksums[od]["md5"]:
                    d_found[idx_d] = True
                    od_found[idx_od] = True

                    # If the names don't match, then append them to the dictionary
                    if not names_match:
                        dat_mappings[d] = od

                    break

        # Save this to yml
        save_yml(out_file, dat_mappings)

        return dat_mappings
