import copy

def split(full_list, chunk_size=10):
    """Split a list in chunks of size chunk_size

    Args:
        full_list (list): list to split
        chunk_size (int, optional): size of each chunk. Defaults to 10
    """

    for i in range(0, len(full_list), chunk_size):
        yield full_list[i:i + chunk_size]


def get_parent_name(game_name,
                    dupe_dict,
                    ):
    """Get the parent name recursively searching through a dupe dict"""

    # We do this by lowercase checking
    reg_dupes = [g for g in dupe_dict]
    all_dupes = [g.lower() for g in dupe_dict]

    # Pull out all the clones so we can check that way as well
    all_clones = [list(dupe_dict[key].keys()) for key in dupe_dict]

    found_dupe = False

    found_parent_name = None

    # First, just check the dupes
    if game_name.lower() in all_dupes:
        found_idx = all_dupes.index(game_name.lower())
        found_parent_name = reg_dupes[found_idx]

        found_dupe = True

    # Check all the clones within the dupes
    else:
        for i, clone in enumerate(all_clones):
            if found_dupe:
                continue

            clone = [c.lower() for c in clone]
            if game_name.lower() in clone:
                found_parent_name = reg_dupes[i]
                found_dupe = True

    if not found_dupe:
        found_parent_name = copy.deepcopy(game_name)

    if found_parent_name is None:
        raise ValueError("Could not find a parent name!")

    return found_parent_name
