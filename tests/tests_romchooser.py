from romsearch import ROMParser, ROMChooser

TEST_NAME = "Example Game"


def test_romchooser_region():
    """Put a number of regions through and check ROMChooser gets the right one"""

    test_case = {
        f"{TEST_NAME} (Europe)": {"priority": 1},
        f"{TEST_NAME} (USA)": {"priority": 1},
    }

    rp = ROMParser(
        config_file="test_config.yml",
        platform="Nintendo - Super Nintendo Entertainment System",
        game="Example Game",
    )
    rom_dict = rp.run(test_case)

    rc = ROMChooser(
        config_file="test_config.yml",
        platform="Nintendo - Super Nintendo Entertainment System",
        game="Example Game",
    )
    rom_dict = rc.run(rom_dict)

    roms_found = [r for r in rom_dict]

    assert roms_found == ["Example Game (USA)"]

def test_romchooser_language():
    """Put a number of languages through and check ROMChooser gets the right one"""

    test_case = {
        f"{TEST_NAME} (En,De)": {"priority": 1},
        f"{TEST_NAME} (Ja)": {"priority": 1},
    }

    rp = ROMParser(
        config_file="test_config.yml",
        platform="Nintendo - Super Nintendo Entertainment System",
        game="Example Game",
    )
    rom_dict = rp.run(test_case)

    rc = ROMChooser(
        config_file="test_config.yml",
        platform="Nintendo - Super Nintendo Entertainment System",
        game="Example Game",
    )
    rom_dict = rc.run(rom_dict)

    roms_found = [r for r in rom_dict]

    assert roms_found == ["Example Game (En,De)"]

def test_romchooser_version():
    """Put a number of versions through and check ROMChooser gets the right one"""

    test_case = {
        TEST_NAME: {"priority": 1},
        f"{TEST_NAME} (v1.00)": {"priority": 1},
        f"{TEST_NAME} (v2.00)": {"priority": 1},
    }

    rp = ROMParser(
        config_file="test_config.yml",
        platform="Nintendo - Super Nintendo Entertainment System",
        game="Example Game",
    )
    rom_dict = rp.run(test_case)

    rc = ROMChooser(
        config_file="test_config.yml",
        platform="Nintendo - Super Nintendo Entertainment System",
        game="Example Game",
    )
    rom_dict = rc.run(rom_dict)

    roms_found = [r for r in rom_dict]

    assert roms_found == ["Example Game (v2.00)"]

def test_romchooser_priority():
    """Put a number of priorities through and check ROMChooser gets the right one"""

    test_case = {
        TEST_NAME: {"priority": 3},
        f"{TEST_NAME} (Higher Priority)": {"priority": 2},
        f"{TEST_NAME} (Highest Priority)": {"priority": 1},
    }

    rp = ROMParser(
        config_file="test_config.yml",
        platform="Nintendo - Super Nintendo Entertainment System",
        game="Example Game",
    )
    rom_dict = rp.run(test_case)

    rc = ROMChooser(
        config_file="test_config.yml",
        platform="Nintendo - Super Nintendo Entertainment System",
        game="Example Game",
    )
    rom_dict = rc.run(rom_dict)

    roms_found = [r for r in rom_dict]

    assert roms_found == ["Example Game (Highest Priority)"]
