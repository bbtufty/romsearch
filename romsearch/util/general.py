import copy
import os
import re
import time
from datetime import datetime


def split(full_list, chunk_size=10):
    """Split a list in chunks of size chunk_size

    Args:
        full_list (list): list to split
        chunk_size (int, optional): size of each chunk. Defaults to 10
    """

    for i in range(0, len(full_list), chunk_size):
        yield full_list[i : i + chunk_size]


def match_retool_search_terms(
    full_name,
    search_term,
    short_name=None,
    region_free_name=None,
    match_type=None,
):
    """Match a name against a search term, given retool's matching rules

    Args:
        full_name (str): Full name for the ROM
        search_term (str): Search term to match against
        short_name (str): Short name to match against. Defaults to None,
            which inherits the full name
        region_free_name (str): Region free name to match against. Defaults to None,
            which inherits the full name
        match_type (str): Type of matching. Defaults to None,
            which will match against short name
    """

    match_found = False

    # Assign default short/region-free names if not supplied
    if short_name is None:
        short_name = copy.deepcopy(full_name)
    if region_free_name is None:
        region_free_name = copy.deepcopy(full_name)

    # If none, match against lowercased short name
    if match_type is None:
        if short_name.lower() == search_term.lower():
            match_found = True

    # If full, match against lowercase full name
    elif match_type == "full":
        if full_name.lower() == search_term.lower():
            match_found = True

    # If region-free, match against lowercased region-free name
    elif match_type == "regionFree":
        if region_free_name.lower() == search_term.lower():
            match_found = True

    # If regex, match against full name
    elif match_type == "regex":
        match = re.search(search_term, full_name)

        if match is not None:
            match_found = True

    else:
        raise ValueError(f"Unsure how to deal with name type {match_type}")

    return match_found


def normalize_name(
    f,
    disc_rename=None,
):
    """Normalize a name to standard form

    Currently, just normalizes the disc name

    Args:
        f (str): Name to normalize
        disc_rename (dict, optional): Disc rename mappings. Defaults to None.
    """

    f_norm = copy.deepcopy(f)

    if disc_rename is not None:
        for k, v in disc_rename.items():
            if k in f_norm:
                f_norm = f_norm.replace(k, v)

    return f_norm


def get_file_time(
    f,
    datetime_format="%Y/%m/%d, %H:%M:%S",
    return_as_str=True,
):
    """Get created file time from the file itself

    Args:
        f (str): Filename
        datetime_format (str, optional): Date and time format. Defaults to "%Y/%m/%d %H:%M:%S"
        return_as_str (bool, optional): Return string or full datetime. Defaults to True
    """

    if os.path.exists(f):
        ti_m = os.path.getmtime(f)
        date_ti_m = datetime.strptime(time.ctime(ti_m), "%a %b %d %H:%M:%S %Y")
    else:
        date_ti_m = datetime(year=1900, month=1, day=1, hour=0, minute=0, second=0)

    if return_as_str:
        date_ti_m_str = date_ti_m.strftime(format=datetime_format)
        return date_ti_m_str
    else:
        return date_ti_m
