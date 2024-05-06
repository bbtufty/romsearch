import glob
import json
import os
from datetime import datetime
from urllib.request import urlopen

import xmltodict

import romsearch
from ..util import load_yml, setup_logger, create_bar, unzip_file, save_json

ALLOWED_GROUPS = [
    "No-Intro",
    "Redump",
]


def get_dat(dat_file_name,
            ):
    """Parse the dat file to a raw dictionary from a zip file"""

    with open(dat_file_name, "r") as f:
        dat = xmltodict.parse(f.read(), attr_prefix='')

    return dat


def format_dat(dat):
    """Format dat into a nice dictionary"""

    rom_dict = {}
    rom_data = dat["datafile"]["game"]

    for rom in rom_data:
        rom_dict[rom["name"]] = rom

    return rom_dict


class DATParser:

    def __init__(self,
                 config_file,
                 platform,
                 ):
        """Parser for dat files from Redump or No-Intro

        For Redump dats, we can download directly from the site.
        Users will have to provide their own files for No-Intro,
        since there's no good way to scrape them automatically
        """

        self.config_file = config_file
        config = load_yml(self.config_file)

        logger_add_dir = str(os.path.join(platform))

        self.logger = setup_logger(log_level="info",
                                   script_name=f"DATParser",
                                   additional_dir=logger_add_dir,
                                   )

        self.dat_dir = config.get("dat_dir", None)
        self.parsed_dat_dir = config.get("parsed_dat_dir", None)

        self.platform = platform

        # Read in the specific platform configuration
        mod_dir = os.path.dirname(romsearch.__file__)
        platform_config_file = os.path.join(mod_dir, "configs", "platforms", f"{self.platform}.yml")
        self.platform_config = load_yml(platform_config_file)

        self.group = self.platform_config.get("group", None)
        if self.group is None:
            raise ValueError("No group name specified in platform config file")
        if self.group not in ALLOWED_GROUPS:
            raise ValueError(f"Group needs to be one of {ALLOWED_GROUPS}")

        # Pull out the platform specifics for the dats
        dat_config_file = os.path.join(mod_dir, "configs", "dats", f"{self.group.lower()}.yml")

        dat_config = load_yml(dat_config_file)
        self.dat_url = dat_config.get("url", None)
        dat_config = dat_config.get(self.platform, None)
        self.dat_config = dat_config

        # Set up the name for the file
        self.out_file = os.path.join(self.parsed_dat_dir, f"{self.platform} (dat parsed).json")

    def run(self):

        self.logger.info(create_bar(f"START DATParser"))

        run_datparser = True

        if self.dat_dir is None:
            self.logger.warning("No dat_dir defined in config file")
            run_datparser = False
        if self.parsed_dat_dir is None:
            self.logger.warning("No parsed_dat_dir defined in config file")
            run_datparser = False
        if self.dat_config is None:
            self.logger.warning("No platform-specific dat config in the dat configuration file")
            run_datparser = False

        if run_datparser:
            self.run_datparser()

        self.logger.info(create_bar(f"FINISH DATParser"))

        return True

    def run_datparser(self):
        """The main meat of running the dat parser"""

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

        rom_dict = format_dat(dat)

        self.save_rom_dict(rom_dict)

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
            self.logger.info(f"Found {len(zip_files)} zip files. Will remove all but the latest (and associated dats)")
            for z in zip_files[:-1]:
                os.remove(z)
                d = z.replace(".zip", ".dat")
                if os.path.exists(d):
                    os.remove(d)

            zip_files = glob.glob(os.path.join(self.dat_dir, f"{file_mapping}*.zip"))
            zip_files.sort()

        if len(zip_files) == 0:
            self.logger.warning(f"No zip files found. "
                                f"You need to manually download {self.group} dat files for {self.platform}")
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
            self.logger.info(f"{f} already downloaded, will skip")
            return True

        self.logger.info(f"Downloading {f}")
        if not os.path.exists(self.dat_dir):
            os.makedirs(self.dat_dir)

        with open(out_file, mode="wb") as d:
            d.write(response.read())

        return True

    def save_rom_dict(self,
                      rom_dict,
                      ):
        """Save the dat file parsed as a dictionary to JSON"""

        if not os.path.exists(self.parsed_dat_dir):
            os.makedirs(self.parsed_dat_dir)

        out_file = os.path.join(self.out_file)
        save_json(rom_dict, out_file)
