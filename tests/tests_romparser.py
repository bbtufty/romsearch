from romsearch import ROMParser

TEST_NAME = "Example Game (USA) (En,De,Fr,Es+It)"


def test_romparser_regions():
    """Put a filename into ROMParser and check it returns the right regions"""

    expected_regions = ["USA"]

    test_case = {TEST_NAME: {"priority": 1}}

    rp = ROMParser(
        config_file="test_config.yml",
        platform="Nintendo - Super Nintendo Entertainment System",
        game="Example Game",
    )
    roms_parsed = rp.run(test_case)

    assert roms_parsed[TEST_NAME]["regions"] == expected_regions


def test_romparser_languages():
    """Put a filename into ROMParser and check it returns the right languages"""

    expected_languages = ["English", "French", "German", "Spanish"]

    test_case = {TEST_NAME: {"priority": 1,
                             "title_pos": 1}
                 }

    rp = ROMParser(
        config_file="test_config.yml",
        platform="Nintendo - Super Nintendo Entertainment System",
        game="Example Game",
    )
    roms_parsed = rp.run(test_case)

    assert roms_parsed[TEST_NAME]["languages"] == expected_languages
