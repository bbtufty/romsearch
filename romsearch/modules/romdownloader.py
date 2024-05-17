import copy
import glob
import os
import subprocess

import romsearch
from ..util import (setup_logger,
                    load_yml,
                    get_file_pattern,
                    discord_push,
                    split,
                    )


def add_rclone_filter(pattern=None,
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

    cmd = f' --filter "{filter_str} {filter_pattern}"'

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

    def __init__(self,
                 platform=None,
                 config_file=None,
                 config=None,
                 platform_config=None,
                 logger=None,
                 override_includes=None,
                 override_excludes=None,
                 include_filter_wildcard=True,
                 ):
        """Downloader tool via rclone

        This works per-platform, so must be specified here

        Args:
            platform (str, optional): Platform name. Defaults to None, which will throw a ValueError
            config (str, optional): Configuration file. Defaults to None
            config (dict, optional): Configuration dictionary. Defaults to None
            platform_config (dict, optional): Platform configuration dictionary. Defaults to None
            logger (logging.Logger, optional): Logger instance. Defaults to None
            override_includes (list, optional): If set, will override the config includes with custom
                ones. Defaults to None.
            override_excludes (list, optional): If set, will override the config excludes with custom
                ones. Defaults to None.
            include_filter_wildcard (bool, optional): If set, will include wildcards in rclone filters. Defaults to
                True.
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
            logger = setup_logger(log_level="info",
                                  script_name=f"ROMDownloader",
                                  log_dir=log_dir,
                                  additional_dir=platform,
                                  )
        self.logger = logger

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

        if override_includes is not None:
            include_games = copy.deepcopy(override_includes)

        self.include_games = include_games

        exclude_games = self.config.get("exclude_games", None)
        if isinstance(exclude_games, dict):
            exclude_games = exclude_games.get(platform, None)
        else:
            exclude_games = copy.deepcopy(exclude_games)

        if override_excludes is not None:
            exclude_games = copy.deepcopy(override_excludes)

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

        self.include_filter_wildcard = include_filter_wildcard

        # Read in the specific platform configuration
        mod_dir = os.path.dirname(romsearch.__file__)

        if platform_config is None:
            platform_config_file = os.path.join(mod_dir, "configs", "platforms", f"{platform}.yml")
            platform_config = load_yml(platform_config_file)
        self.platform_config = platform_config

        ftp_dir = self.platform_config.get("ftp_dir", None)
        if ftp_dir is None:
            raise ValueError(f"ftp_dir should be defined in the platform config file!")
        self.ftp_dir = ftp_dir

        self.discord_url = self.config.get("discord", {}).get("webhook_url", None)
        self.dry_run = self.config.get("romdownloader", {}).get("dry_run", False)

    def run(self,
            ):
        """Run Rclone sync tool"""

        start_files = get_tidy_files(os.path.join(str(self.out_dir), "*"))

        self.rclone_sync(ftp_dir=self.ftp_dir,
                         out_dir=self.out_dir,
                         )

        end_files = get_tidy_files(os.path.join(str(self.out_dir), "*"))

        if self.discord_url is not None:
            name = f"ROMDownloader: {self.platform}"
            self.post_to_discord(start_files,
                                 end_files,
                                 name=name
                                 )

        # If there are potential additional files to download, do that here
        if "additional_dirs" in self.platform_config:

            for add_dir in self.platform_config["additional_dirs"]:
                add_ftp_dir = self.platform_config["additional_dirs"][add_dir]

                add_out_dir = f"{self.out_dir} {add_dir}"

                start_files = get_tidy_files(os.path.join(str(add_out_dir), "*"))

                self.rclone_sync(ftp_dir=add_ftp_dir,
                                 out_dir=add_out_dir,
                                 )

                end_files = get_tidy_files(os.path.join(str(add_out_dir), "*"))

                if self.discord_url is not None:
                    name = f"ROMDownloader: {self.platform} ({add_dir})"
                    self.post_to_discord(start_files,
                                         end_files,
                                         name=name
                                         )

    def rclone_sync(self,
                    ftp_dir,
                    out_dir=None,
                    transfers=5,
                    ):

        if out_dir is None:
            out_dir = os.getcwd()

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        cmd = f'rclone sync -P --transfers {transfers} "{self.remote_name}:{ftp_dir}" "{out_dir}"'

        # We mostly do full syncs here, but we can specify specific game names
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
                cmd += add_rclone_filter(pattern=pattern,
                                         filter_type="exclude",
                                         include_wildcard=self.include_wildcard,
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
                cmd += add_rclone_filter(pattern=pattern,
                                         filter_type="include",
                                         include_wildcard=self.include_filter_wildcard,
                                         )

                cmd += ' --filter "- *"'

        if self.dry_run:
            self.logger.info(f"Dry run, would rclone_sync with:")
            self.logger.info(cmd)
        else:

            if not os.path.exists(self.out_dir):
                os.makedirs(self.out_dir)

            # Execute the command and capture the output
            with subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
                for line in process.stdout:
                    # Log each line of the output using the provided logger
                    self.logger.info(line[:-1])  # Exclude the newline character

        return True

    def post_to_discord(self,
                        start_files,
                        end_files,
                        name,
                        max_per_message=10,
                        ):
        """Create a discord post summarising files added and removed

        Args:
            start_files (list): list of files at the start of the rclone
            end_files (list): list of files at the end of the rclone
            name (string): Name of the post title
            max_per_message (int, optional): Maximum number of items per post. Defaults to 10.
        """

        items_added = list(set(end_files).difference(start_files))
        items_deleted = list(set(start_files).difference(end_files))

        if len(items_added) > 0:

            items_added.sort()

            for items_split in split(items_added, chunk_size=max_per_message):

                fields = []

                field_dict = {"name": "Added",
                              "value": "\n".join(items_split)
                              }
                fields.append(field_dict)

                if len(fields) > 0:
                    discord_push(url=self.discord_url,
                                 name=name,
                                 fields=fields,
                                 )

        if len(items_deleted) > 0:

            items_deleted.sort()

            for items_split in split(items_deleted, chunk_size=max_per_message):

                fields = []

                field_dict = {"name": "Deleted",
                              "value": "\n".join(items_split)
                              }
                fields.append(field_dict)

                if len(fields) > 0:
                    discord_push(url=self.discord_url,
                                 name=name,
                                 fields=fields,
                                 )

        return True
