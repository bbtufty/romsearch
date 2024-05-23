from romsearch import ROMParser, ROMChooser

TEST_NAME = "Example Game (USA) (En,De,Fr)"


def test_romchooser_version():
    """Put a number of versions through and check ROMChooser gets the right one"""

    test_case = {
        TEST_NAME: {"priority": 1},
        f"{TEST_NAME} (v1.00)": {"priority": 1},
        f"{TEST_NAME} (v2.00)": {"priority": 1},
    }

    rp = ROMParser(config_file="test_config.yml",
                   platform="Nintendo - Super Nintendo Entertainment System",
                   game="Example Game",
                   )
    rom_dict = rp.run(test_case)

    rc = ROMChooser(config_file="test_config.yml",
                    platform="Nintendo - Super Nintendo Entertainment System",
                    game="Example Game",
                    )
    rom_dict = rc.run(rom_dict)

    roms_found = [r for r in rom_dict]

    assert roms_found == ["Example Game (USA) (En,De,Fr) (v2.00)"]
