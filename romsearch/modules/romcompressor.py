import glob
import os
import shutil

import subprocess
import re

from ..util import (
    load_yml,
    setup_logger,
    unzip_file,
    centred_string,
)

ALLOWED_COMPRESSION_METHODS = [
    "chdman",
]

CHDMAN_EXTS = [
    "cue",
    "gdi",
]

CUE_FILE_PLATFORMS = [
    "Sony - PlayStation",
]


def create_cue_file(
    rom,
    in_dir=None,
):
    """Create a .cue file for a bunch of files in a directory

    Args:
        rom (str): ROM file
        in_dir (str): Directory containing files to compress. Defaults to None
    """

    orig_dir = None
    if in_dir is not None:
        orig_dir = os.getcwd()
        os.chdir(in_dir)

    # .cue file name
    cue_file_name = os.path.basename(rom)
    cue_file_name = os.path.splitext(cue_file_name)[0]
    cue_file_name = os.path.join(f"{cue_file_name}.cue")

    bin_files = glob.glob("*.bin")
    bin_files.sort()

    # If we don't find any bin files, panic
    if len(bin_files) == 0:
        raise ValueError("No .bin files found in directory")

    # Create the .cue file
    with open(cue_file_name, "w+") as f:

        # Add the first bin file as the main data
        data_file = os.path.basename(bin_files[0])

        f.write(f'FILE "{data_file}" BINARY\n')
        f.write("  TRACK 01 MODE2/2352\n")
        f.write("    INDEX 01 00:00:00\n")

        # And the rest of the bin files as audio
        for i, bin_file in enumerate(bin_files[1:]):

            bin_file = os.path.basename(bin_file)

            f.write(f'FILE "{bin_file}" BINARY\n')

            # Increment by 2 to account for 0-indexing and the fact
            # we've already used the first file
            f.write(f"  TRACK {i+2:02d} AUDIO\n")
            f.write("    INDEX 00 00:00:00\n")
            f.write("    INDEX 01 00:02:00\n")

    # If we've moved, go back to the original directory
    if in_dir is not None:
        os.chdir(orig_dir)
        cue_file_name = os.path.join(in_dir, cue_file_name)

    # Return the .cue file as a list, so it works passing through
    return [cue_file_name]


class ROMCompressor:

    def __init__(
        self,
        platform,
        compress_method="chdman",
        compress_method_path=None,
        config_file=None,
        config=None,
        logger=None,
        log_line_sep="=",
        log_line_length=100,
    ):
        """ROM compression tool

        Offers a way to (re)compress a file. Currently only does CHD compression,
        but can be extended to other compression methods if needed.

        Args:
            platform (str): Platform name
            compress_method (str, optional): compression method. Defaults to "chdman".
            compress_method_path (str, optional): path to compression executable. Defaults to None.
            config_file (str, optional): path to config file. Defaults to None.
            config (dict, optional): configuration dictionary. Defaults to None.
            logger (logging.Logger, optional): logger. Defaults to None.
            log_line_length (int, optional): Line length of log. Defaults to 100
        """

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
                script_name=f"ROMCompressor",
                log_dir=log_dir,
            )
        self.logger = logger

        if compress_method not in ALLOWED_COMPRESSION_METHODS:
            raise ValueError(
                f"compress_method should be one of {ALLOWED_COMPRESSION_METHODS}, not {compress_method}"
            )
        self.compress_method = compress_method

        if compress_method_path is None:
            raise ValueError("compress_method_path must be specified")
        self.compress_method_path = compress_method_path

        # Pull in directories
        compress_dir = self.config.get("dirs", {}).get("compress_dir", None)
        if compress_dir is None:
            raise ValueError("compress_dir needs to be defined in config")

        compress_dir = os.path.join(compress_dir, platform)
        self.compress_dir = compress_dir

        if not os.path.exists(self.compress_dir):
            os.makedirs(self.compress_dir)

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(self, rom):
        """Run the ROMCompressor

        Args:
            rom: ROM file to compress
        """

        # Check if we've already compressed
        rom_no_ext = os.path.splitext(os.path.basename(rom))[0]
        compressed_file = glob.glob(os.path.join(self.compress_dir, f"{rom_no_ext}.*"))

        # If we already have the compressed file, we can return
        if len(compressed_file) == 1:
            compressed_file = compressed_file[0]

        # If we've got nothing, do the compression
        elif len(compressed_file) == 0:

            # Start by unzipping to a temp folder in the compress directory, then do the compression
            temp_dir = os.path.join(self.compress_dir, "temp")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            self.logger.info(
                centred_string(
                    f"Compressing {os.path.basename(rom)} with {self.compress_method}",
                    total_length=self.log_line_length,
                )
            )

            # If we have a zip file, unzip it. Else just move the file
            if rom.endswith(".zip"):
                unzip_file(rom, temp_dir)
            else:
                base_rom = os.path.basename(rom)
                out_rom = os.path.join(temp_dir, base_rom)
                shutil.copy(rom, out_rom)

            if self.compress_method == "chdman":
                compress_files = self.compress_chd(
                    rom=rom,
                    rom_dir=self.compress_dir,
                    temp_dir=temp_dir,
                )

                if len(compress_files) > 1:
                    raise ValueError(f"More compressed files than expected!")

                compressed_file = compress_files[0]

            else:
                raise ValueError(
                    f"compress_method should be one of {ALLOWED_COMPRESSION_METHODS}, "
                    f"not {self.compress_method}"
                )

            # Delete the temp dir
            shutil.rmtree(temp_dir)

        else:

            # If we've found more than one file, freak out
            raise ValueError("Found more files than expected!")

        return compressed_file

    def compress_chd(
        self,
        rom,
        rom_dir,
        temp_dir,
    ):
        """Compress using CHDMAN

        Args:
            rom (str): ROM file to compress
            rom_dir (str): Directory for final, compressed ROM
            temp_dir (str): Directory containing files to compress
        """

        orig_dir = os.getcwd()
        os.chdir(temp_dir)

        # Find the files suitable for CHDMAN compression
        input_files = []
        for ext in CHDMAN_EXTS:
            input_files.extend(glob.glob(f"*.{ext}"))

        # Freak out if we've got more input files than expected
        if len(input_files) > 1:
            raise ValueError(f"More input files than expected!")

        # Alternatively, if we have no files, then create one
        if len(input_files) == 0:
            if self.platform in CUE_FILE_PLATFORMS:
                self.logger.info(
                    centred_string("No .cue file found, creating one",
                                   total_length=self.log_line_length
                                   )
                )
                input_files = create_cue_file(
                    rom=rom,
                )
            else:
                raise ValueError(
                    f"No input files found, and ROMCompressor cannot create files for {self.platform}"
                )

        # Run CHDMAN
        compress_files = []
        for i in input_files:

            # Set up the output filename
            o = os.path.splitext(i)[0]
            o = f"{o}.chd"

            cmd = f'{self.compress_method_path} createcd -i "{i}" -o "{o}"'

            # Execute the command
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

            # Move from temp to ROM dir, then delete
            out_file = os.path.join(rom_dir, o)
            shutil.copy(o, out_file)
            os.remove(o)
            compress_files.append(out_file)

        # Return back to the original directory
        os.chdir(orig_dir)

        return compress_files
