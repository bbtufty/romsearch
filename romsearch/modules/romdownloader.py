import copy
import glob
import numpy as np
import os
import re
import subprocess

import romsearch
from ..util import (
    setup_logger,
    load_yml,
    get_file_pattern,
    discord_push,
    split,
    centred_string,
    remove_case_insensitive_matches,
)

RCLONE_METHODS = [
    "sync",
    "copy",
]


def add_rclone_filter(
    pattern=None,
    filter_type="include",
    include_wildcard=True,
):
    if filter_type == "include":
        filter_str = "+"
    elif filter_type == "exclude":
        filter_str = "-"
    else:
        raise ValueError("filter_type should be one of include or exclude")

    # rclone wants double curly braces which we need to escape in python strings (yum)
    filter_pattern = ""

    if pattern is not None:
        filter_pattern += f"{{{{{pattern}}}}}"

    if include_wildcard:
        filter_pattern += "*"

    cmd = f'--filter "{filter_str} {filter_pattern}" '

    return cmd


def get_tidy_files(glob_pattern):
    """Get a tidy list of files from a glob pattern.

    This just strips off the leading directories to just get a filename

    Args:
        glob_pattern (str): glob pattern to match
    """

    files = glob.glob(glob_pattern)
    files = [os.path.split(f)[-1] for f in files]

    return files


class ROMDownloader:

    def __init__(
        self,
        platform=None,
        config_file=None,
        config=None,
        platform_config=None,
        rclone_method="sync",
        copy_files=None,
        subchannel_dict=None,
        logger=None,
        include_filter_wildcard=True,
        log_line_sep="=",
        log_line_length=100,
    ):
        """Downloader tool via rclone

        This works per-platform, so must be specified here.

        For this, we can either sync an entire directory (rclone_method='sync'), or copy individual files
        (rclone_method='copy'). If the method is copy, then copy_files must be set as a list

        Args:
            platform (str, optional): Platform name. Defaults to None, which will throw a ValueError
            config_file (str, optional): Configuration file. Defaults to None
            config (dict, optional): Configuration dictionary. Defaults to None
            platform_config (dict, optional): Platform configuration dictionary. Defaults to None
            rclone_method (str, optional): Should be one of 'sync' or 'copy'. Defaults to 'sync'
            copy_files (list, optional): Must be set if rclone_method is 'copy'. Determines the filenames to copy over.
                Defaults to None
            subchannel_dict (dict, optional): Dictionary of subchannel files. Defaults to None
            logger (logging.Logger, optional): Logger instance. Defaults to None
            include_filter_wildcard (bool, optional): If set, will include wildcards in rclone filters. Defaults to
                True.
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
                script_name=f"ROMDownloader",
                log_dir=log_dir,
                additional_dir=platform,
            )
        self.logger = logger

        if rclone_method not in RCLONE_METHODS:
            raise ValueError(f"rclone_method must be one of {RCLONE_METHODS}")

        self.rclone_method = rclone_method
        self.copy_files = copy_files
        self.subchannel_dict = subchannel_dict

        out_dir = self.config.get("dirs", {}).get("raw_dir", None)
        if out_dir is None:
            raise ValueError("raw_dir needs to be defined in config")
        self.out_dir = os.path.join(out_dir, platform)

        # Get any specific includes/excludes
        include_games = self.config.get("include_games", None)
        if isinstance(include_games, dict):
            include_games = include_games.get(platform, None)
        else:
            include_games = copy.deepcopy(include_games)

        self.include_games = include_games

        exclude_games = self.config.get("exclude_games", None)
        if isinstance(exclude_games, dict):
            exclude_games = exclude_games.get(platform, None)
        else:
            exclude_games = copy.deepcopy(exclude_games)

        self.exclude_games = exclude_games

        remote_name = self.config.get("romdownloader", {}).get("remote_name", None)
        if remote_name is None:
            raise ValueError("remote_name must be specified in config")
        self.remote_name = remote_name

        sync_all = self.config.get("romdownloader", {}).get("sync_all", True)

        # If we have includes or excludes, force sync all False
        if self.include_games is not None or self.exclude_games is not None:
            sync_all = False

        self.sync_all = sync_all

        # If we're skipping existing files for rclone copy
        skip_existing_files = self.config.get("romdownloader", {}).get(
            "skip_existing_files", True
        )
        self.skip_existing_files = skip_existing_files

        self.include_filter_wildcard = include_filter_wildcard

        # Read in the specific platform configuration
        mod_dir = os.path.dirname(romsearch.__file__)

        if platform_config is None:
            platform_config_file = os.path.join(
                mod_dir, "configs", "platforms", f"{platform}.yml"
            )
            platform_config = load_yml(platform_config_file)
        self.platform_config = platform_config

        remote_dir = self.platform_config.get("dir", None)
        if remote_dir is None:
            raise ValueError(f"dir should be defined in the platform config file!")

        # If we're not using absolute URLs, then remove that here
        self.use_absolute_url = self.config.get("romdownloader", {}).get(
            "use_absolute_url", True
        )
        if not self.use_absolute_url:
            if remote_dir[0] == "/":
                remote_dir = remote_dir[1:]

        self.remote_dir = remote_dir

        self.discord_url = self.config.get("discord", {}).get("webhook_url", None)
        self.dry_run = self.config.get("romdownloader", {}).get("dry_run", False)

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(
        self,
    ):
        """Run Rclone downloader tool"""

        start_files = get_tidy_files(os.path.join(str(self.out_dir), "*"))

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")
        self.logger.info(
            centred_string("Running ROMDownloader", total_length=self.log_line_length)
        )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        self.rclone_download(
            remote_dir=self.remote_dir,
            out_dir=self.out_dir,
        )

        end_files = get_tidy_files(os.path.join(str(self.out_dir), "*"))

        items_added = list(set(end_files).difference(start_files))
        items_added.sort()
        items_deleted = list(set(start_files).difference(end_files))
        items_deleted.sort()

        self.log_items_added_deleted(items_added=items_added,
                                     items_deleted=items_deleted,
                                     )

        if self.discord_url is not None:
            name = f"ROMDownloader: {self.platform}"
            self.post_to_discord(items_added=items_added,
                                 items_deleted=items_deleted,
                                 name=name,
                                 )

        # If there are potential additional files to download, do that here
        if "subchannels" in self.platform_config:

            for sc in self.platform_config["subchannels"]:
                sc_remote_dir = self.platform_config["subchannels"][sc]

                # If using relative URL, strip the leading slash
                if not self.use_absolute_url:
                    if sc_remote_dir[0] == "/":
                        sc_remote_dir = sc_remote_dir[1:]

                sc_out_dir = f"{self.out_dir} {sc}"

                start_files = get_tidy_files(os.path.join(str(sc_out_dir), "*"))

                self.rclone_download(
                    remote_dir=sc_remote_dir,
                    out_dir=sc_out_dir,
                    subchannel=sc,
                    subchannel_original_dir=self.out_dir,
                )

                end_files = get_tidy_files(os.path.join(str(sc_out_dir), "*"))

                items_added = list(set(end_files).difference(start_files))
                items_added.sort()
                items_deleted = list(set(start_files).difference(end_files))
                items_deleted.sort()

                self.log_items_added_deleted(items_added=items_added,
                                             items_deleted=items_deleted,
                                             )

                if self.discord_url is not None:
                    name = f"ROMDownloader: {self.platform} ({sc})"
                    self.post_to_discord(items_added=items_added,
                                         items_deleted=items_deleted,
                                         name=name,
                                         )

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        return True

    def rclone_download(
        self,
        remote_dir,
        out_dir=None,
        subchannel=None,
        subchannel_original_dir=None,
        max_retries=5,
    ):
        """Download from rclone, either via sync or copy

        Args:
            remote_dir: rclone remote path
            out_dir: directory to download to
            subchannel: subchannel to download. Defaults to None
            subchannel_original_dir: Original directory for subchannel-related files. Defaults to None
            max_retries: maximum number of retries
        """

        if out_dir is None:
            out_dir = os.getcwd()

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        if self.rclone_method == "sync":
            self.rclone_sync(
                remote_dir=remote_dir,
                out_dir=out_dir,
                max_retries=max_retries,
            )
        elif self.rclone_method == "copy":
            self.rclone_copy(
                remote_dir=remote_dir,
                out_dir=out_dir,
                subchannel=subchannel,
                subchannel_original_dir=subchannel_original_dir,
                max_retries=max_retries,
            )
        else:
            raise ValueError(f"rclone_method should be one of {RCLONE_METHODS}")

    def rclone_sync(
        self,
        remote_dir,
        out_dir=None,
        transfers=5,
        max_retries=5,
    ):
        """Use rclone to sync an entire directory

        Args:
            remote_dir: rclone remote path
            out_dir: directory to download to
            transfers: number of simultaneous transfers
            max_retries: maximum number of retries
        """

        # Build the sync command. We take the following steps to avoid errors
        # - Disable HTTP2 to avoid GOAWAY errors
        # - Disable multi-thread transfers

        cmd = (
            f"rclone sync "
            f"--inplace "
            f"--fast-list "
            f"--delete-after "
            f"--disable-http2 "
            f"--multi-thread-streams=0 "
            f"--size-only "
            f"--transfers={transfers} "
            f'"{self.remote_name}:{remote_dir}" '
            f'"{out_dir}" '
            f"-v "
        )

        # Include any filters if necessary (which is probably the case)
        if not self.sync_all:

            # Start with any negative filters
            searches = []

            if self.exclude_games is not None:
                searches.extend(self.exclude_games)

            if len(searches) > 0:
                pattern = get_file_pattern(searches)
            else:
                pattern = None

            if pattern:
                cmd += add_rclone_filter(
                    pattern=pattern,
                    filter_type="exclude",
                    include_wildcard=self.include_filter_wildcard,
                )

            # Now onto positive filters
            searches = []

            # Specific games
            if self.include_games is not None:
                searches.extend(self.include_games)

            if len(searches) > 0:
                pattern = get_file_pattern(searches)
            else:
                pattern = None

            if pattern:
                cmd += add_rclone_filter(
                    pattern=pattern,
                    filter_type="include",
                    include_wildcard=self.include_filter_wildcard,
                )

                cmd += '--filter "- *" '

        if self.dry_run:
            self.logger.info(
                centred_string(
                    f"Dry run, would rclone sync with:",
                    total_length=self.log_line_length,
                )
            )
            self.logger.info(centred_string(cmd, total_length=self.log_line_length))
        else:

            retry = 0
            retcode = 1

            self.logger.info(
                centred_string("Running rclone sync", total_length=self.log_line_length)
            )

            while retcode != 0 and retry < max_retries:

                # Execute the command and capture the output
                with subprocess.Popen(
                    cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                ) as process:
                    for line in process.stdout:

                        # Replace any potential tabs in the line, strip whitespace and skip newline at the end
                        line = re.sub(r"\s+", " ", line[:-1])
                        line = line.lstrip().rstrip()

                        if len(line) == 0:
                            continue

                        # Skip the warning about directory filters using regex
                        if "Can't figure out directory filters" in line:
                            continue

                        # Log each line of the output using the provided logger
                        self.logger.info(
                            centred_string(line, total_length=self.log_line_length)
                        )

                retcode = process.poll()
                retry += 1

            # If we've hit the maximum retries and still we have errors, raise an error with the args
            if retcode != 0:
                raise subprocess.CalledProcessError(retcode, process.args)

        return True

    def rclone_copy(
        self,
        remote_dir,
        out_dir=None,
        subchannel=None,
        subchannel_original_dir=None,
        max_retries=5,
    ):
        """Use rclone to copy files one-by-one

        Args:
            remote_dir: rclone remote path
            out_dir: directory to download to
            subchannel: subchannel to copy to
            subchannel_original_dir: Original directory for subchannel-related files. Defaults to None
            max_retries: maximum number of retries
        """

        if self.copy_files is None:
            raise ValueError("copy_files needs to be defined for rclone copy")

        n_files = len(self.copy_files)
        s = f"Downloading {n_files} games"
        if subchannel is not None:
            s += f" ({subchannel})"
        self.logger.info(
            centred_string(
                s,
                total_length=self.log_line_length,
            )
        )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        all_files_to_copy = []

        subchannel_original_files = []
        if subchannel_original_dir is not None:
            subchannel_original_files = [
                os.path.splitext(f)[0]
                for f in get_tidy_files(os.path.join(str(subchannel_original_dir), "*"))
            ]

        for fi, copy_file in enumerate(self.copy_files):

            # If we have a dictionary here, then we have files with priorities, so find the highest
            # priority file that exists on the remote
            if isinstance(self.copy_files, dict):

                priorities = np.unique(
                    [
                        self.copy_files[copy_file][r]["score"]
                        for r in self.copy_files[copy_file]
                    ]
                )[::-1]

            # Otherwise, priorities is just a 0
            else:
                priorities = [0]

            found_files_at_priority = False

            # Loop through priorities and download files at the highest possible priority
            for priority in priorities:

                if found_files_at_priority:
                    continue

                if isinstance(self.copy_files, dict):

                    fs = []

                    for priority_key in self.copy_files[copy_file]:

                        if (
                            self.copy_files[copy_file][priority_key]["score"]
                            != priority
                        ):
                            continue

                        fs.append(self.copy_files[copy_file][priority_key]["name"])

                else:
                    fs = [copy_file]

                all_files_to_copy.extend(fs)

                for f in fs:

                    if subchannel is not None:
                        f_no_ext = os.path.splitext(f)[0]

                        skip_sc = False

                        # If we don't have this file in the subchannel list, then just skip
                        if not f_no_ext in self.subchannel_dict[subchannel]:
                            self.logger.debug(
                                centred_string(
                                    f"{f_no_ext} not found in subchannel files",
                                    total_length=self.log_line_length,
                                )
                            )
                            skip_sc = True

                        # And if we don't have the existing file on disc, also skip
                        if not f_no_ext in subchannel_original_files:
                            self.logger.debug(
                                centred_string(
                                    f"{f_no_ext} not found in original directory",
                                    total_length=self.log_line_length,
                                )
                            )
                            skip_sc = True

                        if skip_sc:
                            all_files_to_copy.remove(f)
                            continue

                    # If we already have the file, then skip if we have that option turned on
                    out_file = os.path.join(out_dir, f)
                    file_already_exists = os.path.exists(out_file)

                    if file_already_exists and self.skip_existing_files:

                        self.logger.info(
                            centred_string(
                                f"[{fi + 1}/{n_files}]: {f} already in {out_dir}, skipping",
                                total_length=self.log_line_length,
                            )
                        )
                        found_files_at_priority = True

                    else:

                        # Check if the file we're trying to download does not match exactly, but does
                        # match in a case-insensitive way, and remove if so
                        f_no_ext = os.path.splitext(f)[0]
                        remove_case_insensitive_matches(file_to_match=f_no_ext,
                                                        pattern=f,
                                                        path=str(out_dir),
                                                        )

                        remote_file_name = f"{self.remote_name}:{remote_dir}{f}"

                        cmd = (
                            f"rclone copy "
                            f"--inplace "
                            f"--no-traverse "
                            f"--disable-http2 "
                            f"--multi-thread-streams=0 "
                            f"--size-only "
                            f'"{remote_file_name}" "{out_dir}" '
                            f"-v "
                        )

                        short_out_dir = os.path.split(out_dir)[-1]

                        if self.dry_run:
                            self.logger.info(
                                centred_string(
                                    f"Dry run, would rclone copy {short_out_dir}: {f} with:",
                                    total_length=self.log_line_length,
                                )
                            )
                            self.logger.info(
                                centred_string(cmd, total_length=self.log_line_length)
                            )
                            found_files_at_priority = True
                        else:

                            retry = 0
                            retcode = 1

                            self.logger.info(
                                centred_string(
                                    f"[{fi + 1}/{n_files}]: Running rclone copy for {short_out_dir}: {f}",
                                    total_length=self.log_line_length,
                                )
                            )

                            # The retcode is set to 9999 if the file doesn't exist
                            while retcode not in [0, 9999] and retry < max_retries:

                                # Execute the command and capture the output
                                with subprocess.Popen(
                                    cmd,
                                    text=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                ) as process:
                                    for line in process.stdout:

                                        # Replace any potential tabs in the line, strip whitespace and skip newline
                                        # at the end
                                        line = re.sub(r"\s+", " ", line[:-1])
                                        line = line.lstrip().rstrip()

                                        if len(line) == 0:
                                            continue

                                        # Skip weird time notifications
                                        if "Time may be set wrong" in line:
                                            continue

                                        # If the file doesn't exist, set a high number and immediately terminate the
                                        # process
                                        if (
                                            "directory not found" in line
                                            or "object not found" in line
                                        ):
                                            retcode = 9999
                                            process.kill()
                                            continue

                                        # Log each line of the output using the provided logger
                                        self.logger.info(
                                            centred_string(
                                                line,  # Exclude the newline character
                                                total_length=self.log_line_length,
                                            )
                                        )

                                if retcode != 9999:
                                    retcode = process.poll()
                                retry += 1

                            # If we've hit the maximum retries and still we have errors, raise an error with the args
                            if retcode not in [0, 9999]:
                                raise subprocess.CalledProcessError(
                                    retcode, process.args
                                )
                            if retcode == 9999:
                                self.logger.warning(
                                    centred_string(
                                        f"Could not find {self.remote_name}:{remote_dir}{f}.",
                                        total_length=self.log_line_length,
                                    )
                                )

                            # Check if the file exists
                            if os.path.exists(out_file):
                                found_files_at_priority = True

            if fi != len(self.copy_files) - 1 and found_files_at_priority:
                self.logger.info(f"{'-' * self.log_line_length}")

        # If we haven't moved anything, note that here
        if len(all_files_to_copy) == 0:
            self.logger.info(
                centred_string(
                    f"No files downloaded",
                    total_length=self.log_line_length,
                )
            )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        # Do a pass through where we delete all extraneous files at the end
        # If we're checking files, then do a pass where if we don't find the file in the includes, then
        # we delete it
        all_files = get_tidy_files(os.path.join(str(out_dir), "*"))

        found_matches = []

        for f in all_files:

            found_match = False

            for c in all_files_to_copy:
                if f == c:
                    found_match = True

            if not found_match:
                os.remove(os.path.join(str(out_dir), f))
                found_matches.append(f)

        return True

    def post_to_discord(
        self,
        items_added,
        items_deleted,
        name,
        max_per_message=10,
    ):
        """Create a discord post summarising files added and removed

        Args:
            items_added (list): list of files added
            items_deleted (list): list of files deleted
            name (string): Name of the post title
            max_per_message (int, optional): Maximum number of items per post. Defaults to 10.
        """

        if len(items_added) > 0:

            for items_split in split(items_added, chunk_size=max_per_message):

                fields = []

                field_dict = {"name": "Added", "value": "\n".join(items_split)}
                fields.append(field_dict)

                if len(fields) > 0:
                    discord_push(
                        url=self.discord_url,
                        name=name,
                        fields=fields,
                    )

        if len(items_deleted) > 0:

            for items_split in split(items_deleted, chunk_size=max_per_message):

                fields = []

                field_dict = {"name": "Deleted", "value": "\n".join(items_split)}
                fields.append(field_dict)

                if len(fields) > 0:
                    discord_push(
                        url=self.discord_url,
                        name=name,
                        fields=fields,
                    )

        return True

    def log_items_added_deleted(self,
                                items_added,
                                items_deleted,
                                ):
        """Log a summary of items added and removed

        Args:
            items_added (list): list of items added
            items_deleted (list): list of items deleted
        """

        if len(items_added) > 0:
            self.logger.info(f"{'-' * self.log_line_length}")
            self.logger.info(
                centred_string(f"Added files:", total_length=self.log_line_length)
            )
            for f in items_added:
                self.logger.info(
                    centred_string(f"{f}", total_length=self.log_line_length)
                )

        if len(items_deleted) > 0:
            self.logger.info(f"{'-' * self.log_line_length}")
            self.logger.info(
                centred_string(f"Removed files:", total_length=self.log_line_length)
            )
            for f in items_deleted:
                self.logger.info(
                    centred_string(f"{f}", total_length=self.log_line_length)
                )

        return True
