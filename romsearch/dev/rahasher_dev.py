import os

from ..util import load_yml, load_json


def check_rahasher_names(config_file, platform):
    """Using a config file and platform, get all applicable RA names with hashes

    Args:
        config_file (string): Path to the config file
        platform (string): Platform name
    """

    config = load_yml(config_file)

    ra_hash_dir = config.get("dirs", {}).get("ra_hash_dir", None)

    if ra_hash_dir is None:
        raise ValueError("No ra_hash_dir found in config file")

    ra_hash_filename = os.path.join(ra_hash_dir, f"{platform}.json")

    if not os.path.exists(ra_hash_filename):
        raise ValueError("No RA hash file found")

    ra_hash_dict = load_json(ra_hash_filename)

    ra_hashes = {}
    for r in ra_hash_dict:
        for h in ra_hash_dict[r]["Hashes"]:
            ra_hashes[h["MD5"]] = {
                "name": h["Name"],
                "hash": h["MD5"],
                "patch_name": h["PatchUrl"],
            }

    return ra_hashes
