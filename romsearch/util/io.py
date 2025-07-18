import copy
import fnmatch
import json
import os
import re
import xmltodict
import yaml
import zipfile


class DumperEdit(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(DumperEdit, self).increase_indent(flow, False)

    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()


def load_yml(f):
    """Load YAML file"""

    with open(f, "r") as file:
        config = yaml.safe_load(file)

    return config


def save_yml(f, data):
    """Save YAML file"""

    with open(f, "w") as file:
        yaml.dump(
            data,
            file,
            Dumper=DumperEdit,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
        )


def unzip_file(
        zip_file_name,
        out_dir,
):
    """Unzip a file"""

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_dir = str(out_dir)

    with zipfile.ZipFile(zip_file_name, "r") as zip_file:
        # Get the names of all the files we're going to extract
        unzipped_files = zip_file.namelist()

        # And extract
        zip_file.extractall(out_dir)

    return unzipped_files


def load_json(file):
    """Load json file"""

    with open(file, "r", encoding="utf-8") as f:
        j = json.load(f)

    return j


def save_json(
        data,
        out_file,
        sort_key=None,
):
    """Save json in a pretty way

    Args:
        data (dict): Data to be saved
        out_file (str): Path to JSON file
        sort_key (str): Key within each dictionary entry to
            sort by. Default is None, which will not sort.
    """

    # Optionally sort this by name
    if sort_key is not None:
        keys = list(data[sort_key].keys())
        keys.sort()

        sorted_data = {key: data[sort_key][key] for key in keys}
        data[sort_key] = sorted_data

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4,
        )


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


def find_files_case_insensitive(pattern, path='.'):
    """Find files in a directory in a case-insensitive manner.

    Args:
        pattern (str): glob pattern to match
        path (str): directory to look for files in (default '.')
    """

    # If the path doesn't exist, return an empty list
    if not os.path.exists(path):
        return []

    rule = re.compile(fnmatch.translate(pattern), re.IGNORECASE)
    return [name for name in os.listdir(path) if rule.match(name)]


def remove_case_insensitive_matches(file_to_match,
                                    pattern,
                                    path=".",
                                    ):
    """Remove files that match, aside from upper/lowercase

    Filesystems can be a bit flaky here about compatibility, so
    force this through

    Args:
        file_to_match (str): Path to file to match, without extension
        pattern (str): glob pattern to match
        path (str): directory to look for files in. Defaults to '.'
    """

    case_insensitive_matches = find_files_case_insensitive(pattern=pattern,
                                                           path=path,
                                                           )
    case_insensitive_matches_no_ext = [os.path.splitext(c)[0] for c in case_insensitive_matches]

    for case_insensitive_match in case_insensitive_matches_no_ext:
        if case_insensitive_match == file_to_match:
            continue

        f_idx = case_insensitive_matches_no_ext.index(case_insensitive_match)
        file_to_remove = copy.deepcopy(case_insensitive_matches[f_idx])
        file_to_remove = os.path.join(path, file_to_remove)

        # For some reason, sometimes this fails, so just keep going
        success = False
        while not success:
            try:
                os.remove(file_to_remove)
                success = True
            except FileNotFoundError:
                pass

    return True
