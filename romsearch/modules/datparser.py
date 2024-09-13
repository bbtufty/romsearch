import glob
import os
from urllib.request import urlopen

import xmltodict

import romsearch
from ..util import centred_string, load_yml, setup_logger, unzip_file, save_json

ALLOWED_GROUPS = [
    "No-Intro",
    "Redump",
]


def get_dat(
    dat_file_name,
):
    """Parse the dat file to a raw dictionary from a zip file"""

    with open(dat_file_name, "r") as f:
        dat = xmltodict.parse(f.read(), attr_prefix="")

    return dat


def format_dat(dat):
    """Format dat into a nice dictionary"""

    rom_dict = {}
    rom_data = dat["datafile"]["game"]

    for rom in rom_data:
        rom_dict[rom["name"]] = rom

    return rom_dict


class DATParser:

    def __init__(
        self,
        platform=None,
        config_file=None,
        config=None,
        platform_config=None,
        logger=None,
        log_line_sep="=",
        log_line_length=100,
    ):
        """Parser for dat files from Redump or No-Intro

        For Redump dats, we can download directly from the site.
        Users will have to provide their own files for No-Intro,
        since there's no good way to scrape them automatically

        Args:
            platform (str, optional): Platform name. Defaults to None, which will throw a ValueError
            config_file (str, optional): Configuration file. Defaults to None
            config (dict, optional): Configuration dictionary. Defaults to None
            platform_config (dict, optional): Platform configuration dictionary. Defaults to None
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

        self.dat_dir = self.config.get("dirs", {}).get("dat_dir", None)
        self.parsed_dat_dir = self.config.get("dirs", {}).get("parsed_dat_dir", None)

        self.platform = platform

        # Read in the specific platform configuration
        mod_dir = os.path.dirname(romsearch.__file__)

        if platform_config is None:
            platform_config_file = os.path.join(
                mod_dir, "configs", "platforms", f"{platform}.yml"
            )
            platform_config = load_yml(platform_config_file)
        self.platform_config = platform_config

        self.group = self.platform_config.get("group", None)
        if self.group is None:
            raise ValueError("No group name specified in platform config file")
        if self.group not in ALLOWED_GROUPS:
            raise ValueError(f"Group needs to be one of {ALLOWED_GROUPS}")

        # Pull out the platform specifics for the dats
        dat_config_file = os.path.join(
            mod_dir, "configs", "dats", f"{self.group.lower()}.yml"
        )

        dat_config = load_yml(dat_config_file)
        self.dat_url = dat_config.get("url", None)
        dat_config = dat_config.get(self.platform, None)
        self.dat_config = dat_config

        # Set up the name for the file
        self.out_file = os.path.join(
            self.parsed_dat_dir, f"{self.platform} (dat parsed).json"
        )

        self.log_line_sep = log_line_sep
        self.log_line_length = log_line_length

    def run(self):

        run_datparser = True
        rom_dict = None

        if self.dat_dir is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    "No dat_dir defined in config file",
                    total_length=self.log_line_length,
                )
            )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_datparser = False
        if self.parsed_dat_dir is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    "No parsed_dat_dir defined in config file",
                    total_length=self.log_line_length,
                )
            )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_datparser = False
        if self.dat_config is None:
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            self.logger.warning(
                centred_string(
                    "No platform-specific dat config in the dat configuration file",
                    total_length=self.log_line_length,
                )
            )
            self.logger.warning(f"{self.log_line_sep * self.log_line_length}")
            run_datparser = False

        if run_datparser:
            rom_dict = self.run_datparser()

        return rom_dict

    def run_datparser(self):
        """The main meat of running the dat parser"""

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")
        self.logger.info(
            centred_string("Running DATParser", total_length=self.log_line_length)
        )
        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        zip_file = self.get_zip_file()
        if zip_file is None:
            return False

        # Unzip the file if it doesn't already exist
        dat_file_name = zip_file.replace(".zip", ".dat")
        if not os.path.exists(dat_file_name):
            unzip_file(zip_file, self.dat_dir)

        dat = get_dat(dat_file_name)

        if dat is None:
            return False

        self.logger.info(f"{'-' * self.log_line_length}")

        self.logger.info(
            centred_string("Using dat file:", total_length=self.log_line_length)
        )
        self.logger.info(
            centred_string(
                f"{os.path.split(dat_file_name)[-1]}", total_length=self.log_line_length
            )
        )

        rom_dict = format_dat(dat)

        self.save_rom_dict(rom_dict)

        self.logger.info(f"{self.log_line_sep * self.log_line_length}")

        return rom_dict

    def get_zip_file(self):
        """Get zip file from the dat directory

        If this is a Redump file, we can download the latest directly from the
        site. Otherwise, you will need to download them manually
        """

        file_mapping = self.dat_config.get("file_mapping", None)
        if file_mapping is None:
            raise ValueError("No file mapping defined in dat config file")

        if self.group == "Redump":
            self.download_latest_redump_dat()

        zip_files = glob.glob(os.path.join(self.dat_dir, f"{file_mapping}*.zip"))
        zip_files.sort()

        if len(zip_files) > 1:

            self.logger.info(
                centred_string(
                    f"Found {len(zip_files)} zip files.",
                    total_length=self.log_line_length,
                )
            )
            self.logger.info(
                centred_string(
                    f"Will remove all but the latest (and associated dats)",
                    total_length=self.log_line_length,
                )
            )

            for z in zip_files[:-1]:
                os.remove(z)
                d = z.replace(".zip", ".dat")
                if os.path.exists(d):
                    os.remove(d)

            zip_files = glob.glob(os.path.join(self.dat_dir, f"{file_mapping}*.zip"))
            zip_files.sort()

        if len(zip_files) == 0:
            self.logger.warning(
                centred_string(
                    f"No zip files found. ", total_length=self.log_line_length
                )
            )
            self.logger.warning(
                centred_string(
                    f"You need to manually download {self.group} dat "
                    f"files for {self.platform}",
                    total_length=self.log_line_length,
                )
            )
            return None

        return zip_files[-1]

    def download_latest_redump_dat(self):
        """Download Redump zip file for the platform"""

        web_mapping = self.dat_config.get("web_mapping", None)
        if web_mapping is None:
            raise ValueError("No web mapping defined in dat config file")

        response = urlopen(f"{self.dat_url}/{web_mapping}")
        f = response.headers.get_filename()

        out_file = os.path.join(self.dat_dir, f)
        if os.path.exists(out_file):
            self.logger.info(
                centred_string(
                    f"{f} already downloaded", total_length=self.log_line_length
                )
            )
            return True

        self.logger.info(
            centred_string(f"Downloading {f}", total_length=self.log_line_length)
        )
        if not os.path.exists(self.dat_dir):
            os.makedirs(self.dat_dir)

        with open(out_file, mode="wb") as d:
            d.write(response.read())

        return True

    def save_rom_dict(
        self,
        rom_dict,
    ):
        """Save the dat file parsed as a dictionary to JSON"""

        if not os.path.exists(self.parsed_dat_dir):
            os.makedirs(self.parsed_dat_dir)

        out_file = os.path.join(self.out_file)
        save_json(rom_dict, out_file)
