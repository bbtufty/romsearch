import json
import os
import zipfile

import yaml


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
        zip_file.extractall(out_dir)

    return True


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
