import copy
import os
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem

import romsearch
from romsearch import ROMSearch
from romsearch.util import load_yml, load_json
from .gui_config import ConfigWindow
from .gui_utils import get_gui_logger


def add_text_to_text_edit(text_edit, text):
    """Add text to textEdit

    Args:
        text_edit (QTextEdit): QTextEdit instance
        text (str): Text to add
    """

    text_edit.append(
        '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">'
        f"{text}"
        "</p>"
        "\n"
    )


def add_underlined_text_to_text_edit(text_edit, text):
    """Add underlined text to textEdit

    Args:
        text_edit (QTextEdit): QTextEdit instance
        text (str): Text to add
    """

    text_edit.append(
        '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">'
        '<span style=" text-decoration: underline;">'
        f"{text}"
        "</span>"
        "</p>"
        "\n"
    )


def add_bold_text_to_text_edit(text_edit, text):
    """Add bold text to textEdit

    Args:
        text_edit (QTextEdit): QTextEdit instance
        text (str): Text to add
    """

    text_edit.append(
        '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">'
        '<span style=" font-weight:700;">'
        f"{text}"
        "</span>"
        "</p>"
        "\n"
    )


class ROMBrowser(QMainWindow):

    def __init__(
        self,
        main_ui,
        config_window=None,
        logger=None,
    ):
        """Class for the ROMBrowser

        Args:
            main_ui: Main window
            config_window: Config window. Defaults to None,
                which will set it up
            logger: Logger object. Defaults to None, which will load
                some default
        """

        super().__init__()

        self.ui = main_ui

        if logger is None:
            log_level = (
                self.ui.radioButtonConfigLoggerLevel.checkedButton().text().lower()
            )
            logger = get_gui_logger(log_level=log_level)
        self.logger = logger

        # Set up the config window if we haven't already
        if config_window is None:
            config_window = ConfigWindow(self.ui, logger=self.logger)
        self.config_window = config_window

        # Load in any configs we might need
        self.mod_dir = os.path.dirname(romsearch.__file__)

        default_file = os.path.join(self.mod_dir, "configs", "defaults.yml")
        default_config = load_yml(default_file)
        self.default_config = default_config

        rom_regex_file = os.path.join(self.mod_dir, "configs", "gui", "rom_regex.yml")
        rom_regex_config = load_yml(rom_regex_file)
        self.rom_regex_config = rom_regex_config

        # Set up the ROMs list
        self.setup_platforms_list()
        self.ui.comboBoxRomBrowserPlatform.activated.connect(self.load_roms)

        # Set up the search bar
        self.search_bar = self.ui.lineEditRomBrowserSearch
        self.search_bar.textChanged.connect(self.search_bar_update)

        # Info about the actual games and ROMs
        self.current_platform = None
        self.parsed = {}
        self.all_dats = {}
        self.all_dupes = {}
        self.all_retool = {}
        self.all_ra_hash = {}
        self.all_games = {}

        # Cache
        self.cache = {}

    def setup_platforms_list(self):
        """Load a list of platforms"""

        # Clear anything that might already be there
        self.ui.comboBoxRomBrowserPlatform.clear()

        # Set platforms
        for platform in self.default_config["platforms"]:
            platform_item = self.tr(platform)
            self.ui.comboBoxRomBrowserPlatform.addItem(platform_item)

    def load_roms(self):
        """Load ROMs into the Platform table"""

        self.current_platform = self.ui.comboBoxRomBrowserPlatform.currentText()

        # Clear our the search bar and table if anything exists already
        self.search_bar.clear()
        tree_widget = self.ui.treeWidgetRomBrowser
        tree_widget.clear()

        # Set the header to a platform
        tree_widget.setHeaderLabel(self.tr(self.current_platform))

        # We can cache these dictionaries for speed
        if self.current_platform not in self.all_games:
            self.logger.info("Getting all games. UI may become unresponsive")

            self.ui.centralwidget.setEnabled(False)
            QApplication.processEvents()

            # Get the name for the config file
            config_file = self.ui.lineEditConfigConfigFile.text()

            rs = ROMSearch(
                config_file,
                logger=self.logger,
            )

            dat_dict, subchannel_dict, dupe_dict, retool_dict, ra_hash_dict, all_games = (
                rs.get_all_games(
                    platform=self.current_platform,
                )
            )

            self.ui.centralwidget.setEnabled(True)
            QApplication.processEvents()

            self.parsed[self.current_platform] = {}
            self.all_dats[self.current_platform] = copy.deepcopy(dat_dict)
            self.all_dupes[self.current_platform] = copy.deepcopy(dupe_dict)
            self.all_retool[self.current_platform] = copy.deepcopy(retool_dict)
            self.all_ra_hash[self.current_platform] = copy.deepcopy(ra_hash_dict)
            self.all_games[self.current_platform] = copy.deepcopy(all_games)

            for g in self.all_games[self.current_platform]:
                self.parsed[self.current_platform][g] = False

            # Pull out the cache, if it exists
            cache_dir = rs.config.get("dirs", {}).get("cache_dir", os.getcwd())
            cache_file = os.path.join(
                cache_dir, f"cache ({self.current_platform}).json"
            )
            if os.path.exists(cache_file):
                cache = load_json(cache_file)
                cache = copy.deepcopy(cache[self.current_platform])
            else:
                cache = {}
            self.cache[self.current_platform] = copy.deepcopy(cache)

        self.set_games(all_games=self.all_games[self.current_platform])

    def set_games(
        self,
        all_games,
    ):
        """Set all games in the tree

        Args:
            all_games: Dictionary of all games
        """

        # Clear our the table if anything exists already
        tree_widget = self.ui.treeWidgetRomBrowser
        tree_widget.clear()

        for g in all_games:

            game_item = QTreeWidgetItem()
            game_item.setText(0, self.tr(g))

            # Check if game is in cache, and colour if so
            game_in_cache = self.cache.get(self.current_platform, {}).get(g, None)
            if game_in_cache is not None:
                game_item.setBackground(0, QColor(0, 255, 0, 50))

            for i, r in enumerate(all_games[g]):
                rom_item = QTreeWidgetItem()
                rom_item.setText(0, self.tr(r))
                game_item.addChild(rom_item)

                # Check if ROM is in cache, and colour if so
                if game_in_cache is not None:
                    rom_in_cache = (
                        self.cache.get(self.current_platform, {})
                        .get(g, {})
                        .get(r, None)
                    )
                    if rom_in_cache is not None:
                        rom_item.setBackground(0, QColor(0, 255, 0, 50))

            tree_widget.addTopLevelItem(game_item)

        # Set this up to update the ROM descriptions
        tree_widget.itemClicked.connect(self.rom_descriptions_update)

    def search_bar_update(self, text):
        """When using the search bar, show/hide rows

        Args:
            text (str): Text to filter out rows
        """

        # Can only do this if we've got a platform selected
        if self.current_platform is not None:
            # This is a little tricky, since we can't just hide and reshow things.
            # Instead, loop over and set up a new dictionary, then remake the table
            all_games = {}

            for g in self.all_games[self.current_platform]:
                if text.lower() in g.lower():
                    all_games[g] = self.all_games[self.current_platform][g]

            self.set_games(all_games=all_games)

    def rom_descriptions_update(self):
        """Update ROM descriptions text field

        This is different to whether we're clicking a top-level parent or
        child ROM item, so check first and siphon off
        """

        tree_widget = self.ui.treeWidgetRomBrowser
        self.ui.textBrowserRomBrowserRomDescriptions.clear()

        if tree_widget.currentItem().parent() is None:
            self.rom_descriptions_update_game()
        else:
            self.rom_descriptions_update_rom()

    def rom_descriptions_update_game(self):
        """Update ROM descriptions for top-level game"""

        tree_widget = self.ui.treeWidgetRomBrowser
        rom_descriptions = self.ui.textBrowserRomBrowserRomDescriptions

        game = tree_widget.currentItem().text(0)

        # Add game name, followed by the various aliases
        add_underlined_text_to_text_edit(rom_descriptions, f"Game: {game}")
        rom_descriptions.append("<br>")

        add_bold_text_to_text_edit(rom_descriptions, f"Aliases:")

        if game in self.all_dupes[self.current_platform]:
            for g in self.all_dupes[self.current_platform][game]:
                add_text_to_text_edit(rom_descriptions, f"  {g}")
        else:
            add_text_to_text_edit(rom_descriptions, f"  No aliases found")

    def rom_descriptions_update_rom(self):
        """Update ROM descriptions for ROM item"""

        tree_widget = self.ui.treeWidgetRomBrowser
        rom_descriptions = self.ui.textBrowserRomBrowserRomDescriptions

        game = tree_widget.currentItem().parent().text(0)
        rom = tree_widget.currentItem().text(0)

        # Parse the ROMs if we haven't already
        if not self.parsed[self.current_platform][game]:

            rom_files = self.all_games[self.current_platform][game]

            # Get the name for the config file
            config_file = self.ui.lineEditConfigConfigFile.text()

            rs = ROMSearch(
                config_file,
                logger=self.logger,
            )

            platform_config = rs.get_platform_config(self.current_platform)

            rom_dict = rs.run_romparser(
                rom_files=rom_files,
                platform=self.current_platform,
                game=game,
                dat=self.all_dats[self.current_platform],
                retool=self.all_retool[self.current_platform],
                ra_hash=self.all_ra_hash[self.current_platform],
                platform_config=platform_config,
                log_line_length=100,
            )

            self.all_games[self.current_platform][game] = copy.deepcopy(rom_dict)
            self.parsed[self.current_platform][game] = True

        # Add ROM name, followed by parsed ROM details
        add_underlined_text_to_text_edit(rom_descriptions, f"Game: {game}")
        rom_descriptions.append("<br>")
        add_bold_text_to_text_edit(rom_descriptions, f"ROM: {rom}")
        rom_descriptions.append("<br>")

        parsed_keys = copy.deepcopy(self.all_games[self.current_platform][game][rom])

        for k in self.rom_regex_config:
            if k in parsed_keys:
                format_name = copy.deepcopy(self.rom_regex_config[k]["formatted_name"])
                text = copy.deepcopy(parsed_keys[k])

                # If we have a list, format it nicely
                if isinstance(text, list):
                    text = ", ".join(text)

                add_text_to_text_edit(rom_descriptions, f"{format_name}: {text}")

        rom_descriptions.append("<br>")
