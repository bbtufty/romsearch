import copy
from urllib import parse as urlparse

import glob
import os
import re
import shutil
import subprocess
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
    "rompatcher.js",
]


def find_file_by_extensions(
    file_exts,
    patch_dir,
):
    """Find a file by extension

    Args:
        file_exts (list): File extensions to loop over
        patch_dir (str): Patch directory
    """

    files = []

    for file_ext in file_exts:
        file = glob.glob(os.path.join(patch_dir, f"*{file_ext}"))
        files.extend(file)

    return files


class ROMPatcher:

    def __init__(
        self,
        platform,
        config_file=None,
        config=None,
        platform_config=None,
        regex_config=None,
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
            regex_config (dict, optional): regex configuration dictionary. Defaults to None.
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

        # Read in the various pre-set configs we've got
        mod_dir = os.path.dirname(romsearch.__file__)

        if regex_config is None:
            regex_file = os.path.join(mod_dir, "configs", "regex.yml")
            regex_config = load_yml(regex_file)
        self.regex_config = regex_config

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(
        self,
        file,
        patch_url,
        rom_dict=None,
    ):
        """Run the ROMPatcher

        Args:
            file (str): file to patch
            patch_url (str): URL for patch files
            rom_dict: Parsed ROM dictionary
        """

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
        
        # If we don't find a patch in the base directory, search
        # via various conditions. For now, just revision
        if len(patch_file) == 0:

            if rom_dict is not None:
                revision = rom_dict["revision"]
                if revision == "":
                    revision = "v1"
            else:
                raise ValueError("Searching for patch files requires ROM parsing!")

            patch_subdirs = [x[0] for x in os.walk(patch_dir)]

            found_patch = False
            for patch_subdir in patch_subdirs:

                if found_patch:
                    continue

                rel_patch_subdir = os.path.basename(patch_subdir)

                # Search by revision
                if "rev" in rel_patch_subdir.lower():
                    rev_dir_parsed = re.sub(
                        self.regex_config["revision"]["transform_pattern"],
                        self.regex_config["revision"]["transform_repl"],
                        rel_patch_subdir,
                    )
                    if revision == rev_dir_parsed:
                        patch_file = self.find_patch_file(patch_subdir)
                        if len(patch_file) > 0:
                            found_patch = True

                # Otherwise, give up and move on
                else:
                    continue

        # If we have multiple potential patch files, try and find one
        # that matches the name most closely
        if len(patch_file) > 1:
            best_patch_file = None

            base_file = os.path.basename(file)
            base_file = os.path.splitext(base_file)[0]

            for p in patch_file:

                if best_patch_file is not None:
                    continue

                base_patch_file = os.path.basename(p)

                if base_file in base_patch_file:
                    best_patch_file = p

            if best_patch_file is not None:
                patch_file = copy.deepcopy(best_patch_file)
            else:
                pretty_patch_files = [os.path.basename(p) for p in patch_file]
                raise ValueError(
                    f"Could not find suitable patch file in {pretty_patch_files}"
                )

        elif len(patch_file) == 1:
            patch_file = patch_file[0]

        else:
            raise ValueError("No patch files found!")

        # Now we have everything we need to patch this ROM
        patched_file = self.patch_rom(
            unpatched_file=unpatched_file,
            patch_dir=patch_dir,
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

        # If we've got more than one ROM file, error out
        if len(rom_file) > 1:
            raise ValueError("Cannot handle multiple ROM files!")

        rom_file = rom_file[0]

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

        # Since the URL can already have the % in, unquote before passing to wget
        patch_file = wget.download(urlparse.unquote(patch_url), out=patch_dir)
        if patch_file.endswith(".zip"):
            unzip_file(patch_file, patch_dir)

        patch_file = self.find_patch_file(patch_dir=patch_dir)

        return patch_file

    def find_patch_file(
            self,
            patch_dir,
    ):
        """ Find potentially multiple patch files within directory

        Args:
            patch_dir (str): Patch directory to search
        """

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

    def patch_rom(
        self,
        unpatched_file,
        patch_file,
        patch_dir,
    ):
        """Patch a ROM

        Args:
            unpatched_file (str): ROM file to patch
            patch_file (str): Patch file to patch
            patch_dir (str): Patch directory
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
        elif patch_method == "rompatcher.js":

            rompatcher_js_file = (
                f"{unpatch_file_split[0]} (patched){unpatch_file_split[1]}"
            )

            self.rompatcher_js_patch(
                unpatched_file=unpatched_file,
                patch_file=patch_file,
                rompatcher_js_file=rompatcher_js_file,
                out_file=patched_file,
                patch_dir=patch_dir,
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

    def rompatcher_js_patch(
        self,
        unpatched_file,
        patch_file,
        rompatcher_js_file,
        out_file,
        patch_dir,
    ):
        """Patch using RomPatcher.js

        Args:
            unpatched_file (str): ROM file to patch
            patch_file (str): Patch file to patch
            rompatcher_js_file (str): Filename that RomPatcher.js will output
            out_file (str): Path for output file
            patch_dir (str): Patch directory
        """

        rompatcher_js_path = self.config.get("rompatcher", {}).get(
            "rompatcher_js_path", None
        )

        if rompatcher_js_path is None:
            raise ValueError("Path to RomPatcher.js needs to be defined in user config")

        if not os.path.exists(rompatcher_js_path):
            raise ValueError("RomPatcher.js path not found")

        cmd = f'node {rompatcher_js_path} patch "{unpatched_file}" "{patch_file}"'

        self.logger.info(
            centred_string(
                f"Patching file with RomPatcher.js:",
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
                f"-> RomPatcher.js file: {os.path.basename(rompatcher_js_file)}",
                total_length=self.log_line_length,
            )
        )

        # Change to patch directory so file ends up in a sensible spot
        orig_dir = os.getcwd()
        os.chdir(patch_dir)

        with subprocess.Popen(
            cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        ) as process:
            for line in process.stdout:

                # Replace any potential tabs in the line, strip whitespace and skip newline at the end
                line = re.sub(r"\s+", " ", line[:-1])
                line = line.lstrip().rstrip()

                if len(line) == 0:
                    continue

                # Log each line of the output using the provided logger
                self.logger.info(
                    centred_string(line, total_length=self.log_line_length)
                )

        # Return to working directory
        os.chdir(orig_dir)

        self.logger.info(
            left_aligned_string(
                f"-> Renaming file to: {os.path.basename(out_file)}",
                total_length=self.log_line_length,
            )
        )

        shutil.copy(rompatcher_js_file, out_file)
        os.remove(rompatcher_js_file)

        return True
