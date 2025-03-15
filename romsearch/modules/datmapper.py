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

        # Keep track of ones we've matched for speed, since they should be unique
        d_found = [False] * len(dat)
        od_found = [False] * len(old_dat)

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

                # If we already have an exact name match, skip
                if d == od:
                    d_found[idx_d] = True
                    od_found[idx_od] = True
                    continue

                # Get list of ROM files out
                d_roms = dat[d]["rom"]
                od_roms = old_dat[od]["rom"]

                if isinstance(d_roms, dict):
                    d_roms = [d_roms]
                if isinstance(od_roms, dict):
                    od_roms = [od_roms]

                # If we don't have the same number of files, skip
                if len(d_roms) != len(od_roms):
                    continue

                # Compare by MD5 checksums
                d_md5s = [d_rom["md5"].lower() for d_rom in d_roms]
                d_md5s.sort()
                od_md5s = [od_rom["md5"].lower() for od_rom in od_roms]
                od_md5s.sort()

                # If we have a match and the name is different, then append to dictionary and mark as found
                if d_md5s == od_md5s:
                    d_found[idx_d] = True
                    od_found[idx_od] = True
                    dat_mappings[d] = od

        # Save this to yml
        save_yml(out_file, dat_mappings)

        return dat_mappings
