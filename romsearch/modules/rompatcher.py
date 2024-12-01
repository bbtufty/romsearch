import glob
import os
import shutil

import wget

import romsearch
from ..util import (
    load_yml,
    setup_logger,
    unzip_file,
    centred_string,
    left_aligned_string,
)

ALLOWED_PATCH_METHODS = [
    "xdelta",
]


def find_file_by_extensions(file_exts, patch_dir):
    """Find a file by extension

    Args:
        file_exts (list): File extensions to loop over
        patch_dir (str): Patch directory
    """

    potential_files = []

    for file_ext in file_exts:
        potential_file = glob.glob(os.path.join(patch_dir, f"*{file_ext}"))
        potential_files.extend(potential_file)

    # If we have multiple potential files, then error out
    if len(potential_files) > 1:
        raise ValueError(f'Multiple files found: {", ".join(potential_files)}')

    file = potential_files[0]

    return file


class ROMPatcher:

    def __init__(
        self,
        platform,
        config_file=None,
        config=None,
        platform_config=None,
        logger=None,
        log_line_sep="=",
        log_line_length=100,
    ):
        """ROM Patching tool

        There are different ways to patch files based on platforms, so we need
        to keep track of a number of things here

        Args:
            platform (str): Platform name
            config_file (str, optional): path to config file. Defaults to None.
            config (dict, optional): configuration dictionary. Defaults to None.
            platform_config (dict, optional): platform configuration dictionary. Defaults to None.
            logger (logging.Logger, optional): logger. Defaults to None.
            log_line_length (int, optional): Line length of log. Defaults to 100
        """

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
                script_name=f"ROMPatcher",
                log_dir=log_dir,
            )
        self.logger = logger

        # Pull in directories
        self.patch_dir = self.config.get("dirs", {}).get("patch_dir", None)
        if self.patch_dir is None:
            raise ValueError("patch_dir needs to be defined in config")

        if not os.path.exists(self.patch_dir):
            os.makedirs(self.patch_dir)

        self.platform = platform

        # Pull in platform config that we need
        mod_dir = os.path.dirname(romsearch.__file__)

        if platform_config is None:
            platform_config_file = os.path.join(
                mod_dir, "configs", "platforms", f"{platform}.yml"
            )
            platform_config = load_yml(platform_config_file)
        self.platform_config = platform_config

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(
        self,
        file,
        patch_url,
    ):
        """Run the ROMPatcher"""

        filename_no_ext = os.path.splitext(os.path.basename(file))[0]
        patch_dir = str(os.path.join(self.patch_dir, self.platform, filename_no_ext))

        # Clean out and create patch directory
        if os.path.exists(patch_dir):
            shutil.rmtree(patch_dir)
        if not os.path.exists(patch_dir):
            os.makedirs(patch_dir)

        # Move and unzip file, if needed
        self.logger.info(
            centred_string(
                f"Moving {file} to {patch_dir}",
                total_length=self.log_line_length,
            )
        )

        # If we have a zip, unzip that cutie
        if file.endswith(".zip"):
            unzip_file(file, patch_dir)
        else:
            ensure_directory = ""
            if not self.patch_dir.endswith(os.path.sep):
                ensure_directory = os.path.sep
            shutil.copy(file, patch_dir + ensure_directory)

        # Find the unpatched file
        unpatched_file = self.get_unpatched_file(patch_dir=patch_dir)

        # Next up, download the patch file
        patch_file = self.download_patch_file(
            patch_url,
            patch_dir=patch_dir,
        )

        # Now we have everything we need to patch this ROM
        patched_file = self.patch_rom(
            unpatched_file=unpatched_file,
            patch_file=patch_file,
        )

        return patched_file

    def get_unpatched_file(
        self,
        patch_dir,
    ):
        """Get the unpatched file from the patch directory

        Args:
            patch_dir (str): Patch directory
        """

        file_exts = self.platform_config.get("file_exts", [])

        # Error if we don't have file extensions defined
        if len(file_exts) == 0:
            raise ValueError(
                "File extensions need to be defined in the platform config file"
            )

        rom_file = find_file_by_extensions(
            file_exts=file_exts,
            patch_dir=patch_dir,
        )

        return rom_file

    def download_patch_file(
        self,
        patch_url,
        patch_dir,
    ):
        """Download a patch file

        Args:
            patch_url (str): URL to patch file
            patch_dir (str): Patch directory
        """

        self.logger.info(
            centred_string(
                f"Downloading patch file: {patch_url}",
                total_length=self.log_line_length,
            )
        )

        patch_file = wget.download(patch_url, out=patch_dir)
        if patch_file.endswith(".zip"):
            unzip_file(patch_file, patch_dir)

        # Find the patch file
        patch_file_exts = self.platform_config.get("patch_file_exts", [])

        # Error if we don't have patch file extensions defined
        if len(patch_file_exts) == 0:
            raise ValueError(
                "Patch file extensions need to be defined in the platform config file"
            )

        patch_file = find_file_by_extensions(
            patch_file_exts,
            patch_dir=patch_dir,
        )

        return patch_file

    def patch_rom(self, unpatched_file, patch_file):
        """Patch a ROM

        Args:
            unpatched_file (str): ROM file to patch
            patch_file (str): Patch file to patch
        """

        # Get the method we're using to patch things
        patch_method = self.platform_config.get("patch_method", None)

        # Error out if the patch method is not defined
        if patch_method is None:
            raise ValueError(
                "Patch method needs to be defined in the platform config file"
            )

        # Build an output file, adding a (ROMPatched) to the bit before the file extension
        unpatch_file_split = os.path.splitext(unpatched_file)
        patched_file = f"{unpatch_file_split[0]} (ROMPatched){unpatch_file_split[1]}"

        if patch_method == "xdelta":
            self.xdelta_patch(
                unpatched_file=unpatched_file,
                patch_file=patch_file,
                out_file=patched_file,
            )
        else:
            raise ValueError(
                f"Patch method needs to be one of {', '.join(ALLOWED_PATCH_METHODS)}, not {patch_method}"
            )

        self.logger.info(
            centred_string(
                f"Patching complete!",
                total_length=self.log_line_length,
            )
        )

        return patched_file

    def xdelta_patch(
        self,
        unpatched_file,
        patch_file,
        out_file,
    ):
        """Patch using xdelta

        Args:
            unpatched_file (str): ROM file to patch
            patch_file (str): Patch file to patch
            out_file (str): Path for output file
        """

        xdelta_path = self.config.get("rompatcher", {}).get("xdelta_path", None)

        if xdelta_path is None:
            raise ValueError("Path to xdelta needs to be defined in user config")

        if not os.path.exists(xdelta_path):
            raise ValueError("xdelta path not found")

        cmd = f'{xdelta_path} -d -s "{unpatched_file}" "{patch_file}" "{out_file}"'

        self.logger.info(
            centred_string(
                f"Patching file with xdelta:",
                total_length=self.log_line_length,
            )
        )
        self.logger.info(
            left_aligned_string(
                f"-> Unpatched file: {os.path.basename(unpatched_file)}",
                total_length=self.log_line_length,
            )
        )
        self.logger.info(
            left_aligned_string(
                f"-> Patch file: {os.path.basename(patch_file)}",
                total_length=self.log_line_length,
            )
        )
        self.logger.info(
            left_aligned_string(
                f"-> Output file: {os.path.basename(out_file)}",
                total_length=self.log_line_length,
            )
        )

        os.system(cmd)

        return True
