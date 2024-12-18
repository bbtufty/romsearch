import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QPlainTextEdit,
)
from functools import partial

import romsearch
from romsearch.util import load_yml, save_yml, load_json, save_json
from .gui_utils import add_item_to_list, get_gui_logger


def set_ordered_list(
    list_widget,
    item_dict,
    items,
):
    """Set checked items from an ordered list

    Args:
        list_widget (QListWidget): The QListWidget
        item_dict (dict): A dictionary of items that contains the list items to index
        items (list): A list of items to set checked, in order
    """

    # Set the items to checked
    for i in items:
        item_dict[i]["item"].setCheckState(Qt.CheckState.Checked)
        item_dict[i]["check_state"] = True

    # Move the items into order
    for i in items[::-1]:
        idx = list_widget.row(item_dict[i]["item"])
        take_item = list_widget.takeItem(idx)
        list_widget.insertItem(0, take_item)
        list_widget.setCurrentRow(0)

    return True


def add_include_exclude_layout(
    tab_config,
    text="Includes",
):
    """Add the include/exclude table

    Args:
        tab_config (QWidget): The table widget to add the left/right tables to
        text (str): The text to put on top of the text edit
    """

    font = QFont()
    font.setBold(True)

    # Excludes
    hlayout = QHBoxLayout()
    vlayout = QVBoxLayout()

    label_exclude = QLabel(tab_config)
    label_exclude.setText(text)
    label_exclude.setFont(font)
    label_exclude.setAlignment(Qt.AlignmentFlag.AlignCenter)
    vlayout.addWidget(label_exclude)

    line = QFrame(tab_config)
    line.setFrameShadow(QFrame.Shadow.Plain)
    line.setFrameShape(QFrame.Shape.HLine)
    vlayout.addWidget(line)

    text_edit = QPlainTextEdit(tab_config)
    text_edit.setFrameShape(QFrame.Shape.WinPanel)
    text_edit.setFrameShadow(QFrame.Shadow.Plain)
    vlayout.addWidget(text_edit)

    hlayout.addLayout(vlayout)

    return text_edit, hlayout


class ConfigWindow(QMainWindow):

    def __init__(
        self,
        main_ui,
        logger=None,
    ):
        """Class for the configuration window"""

        super().__init__()

        self.ui = main_ui

        if logger is None:
            log_level = (
                self.ui.radioButtonConfigLoggerLevel.checkedButton().text().lower()
            )
            logger = get_gui_logger(log_level=log_level)
        self.logger = logger

        # Read in the various pre-set configs we've got
        self.mod_dir = os.path.dirname(romsearch.__file__)

        default_file = os.path.join(self.mod_dir, "configs", "defaults.yml")
        default_config = load_yml(default_file)
        self.default_config = default_config

        self.config = {}

        self.include_exclude_dict = {}

        # Set up platforms
        self.platform_items = self.populate_list(
            "platforms",
            self.ui.listWidgetConfigPlatforms,
            check_state=False,
        )

        self.ui.listWidgetConfigPlatforms.itemChanged.connect(
            self.get_platforms_changed
        )

        # Set up regions/languages
        self.region_items = self.populate_list(
            "regions",
            self.ui.listWidgetConfigRegionsLanguagesRegions,
            check_state=False,
        )
        self.language_items = self.populate_list(
            "languages",
            self.ui.listWidgetConfigRegionsLanguagesLanguages,
            check_state=False,
        )

        # Set up groupings for later
        self.all_dirs = {
            "raw_dir": self.ui.lineEditConfigRawDir,
            "rom_dir": self.ui.lineEditConfigRomDir,
            "patch_dir": self.ui.lineEditConfigPatchDir,
            "ra_hash_dir": self.ui.lineEditConfigRAHashDir,
            "dat_dir": self.ui.lineEditConfigDatDir,
            "parsed_dat_dir": self.ui.lineEditConfigParsedDatDir,
            "dupe_dir": self.ui.lineEditConfigDupeDir,
            "cache_dir": self.ui.lineEditConfigCacheDir,
            "log_dir": self.ui.lineEditConfigLogDir,
        }

        self.all_dirs_buttons = {
            "raw_dir": self.ui.pushButtonConfigRawDir,
            "rom_dir": self.ui.pushButtonConfigRomDir,
            "patch_dir": self.ui.pushButtonConfigPatchDir,
            "ra_hash_dir": self.ui.pushButtonConfigRAHashDir,
            "dat_dir": self.ui.pushButtonConfigDatDir,
            "parsed_dat_dir": self.ui.pushButtonConfigParsedDatDir,
            "dupe_dir": self.ui.pushButtonConfigDupeDir,
            "cache_dir": self.ui.pushButtonConfigCacheDir,
            "log_dir": self.ui.pushButtonConfigLogDir,
        }
        # Get the buttons hooked up to the line edits. Because we're looping, lambda can get wonky so use partial
        for b in self.all_dirs_buttons:
            self.all_dirs_buttons[b].clicked.connect(
                partial(self.set_directory_name, line_edit=self.all_dirs[b])
            )

        # Do the same for the directories, but for files instead
        self.all_files = {
            "xdelta_path": self.ui.lineEditConfigRomPatcherxdeltaPath,
            "rompatcher_js_path": self.ui.lineEditConfigRomPatcherRomPatcherjsPath,
        }
        self.all_files_buttons = {
            "xdelta_path": self.ui.pushButtonConfigRomPatcherxdeltaPath,
            "rompatcher_js_path": self.ui.pushButtonConfigRomPatcherRomPatcherjsPath,
        }
        for b in self.all_files_buttons:
            self.all_files_buttons[b].clicked.connect(
                partial(self.set_file_name, line_edit=self.all_files[b])
            )

        self.romdownloader_text_fields = {
            "remote_name": self.ui.lineEditConfigRomDownloaderRemoteName,
        }

        self.rahasher_text_fields = {
            "username": self.ui.lineEditConfigRAHasherUsername,
            "api_key": self.ui.lineEditConfigRAHasherAPIKey,
            "cache_period": self.ui.lineEditConfigRAHasherCachePeriod,
        }

        self.rompatcher_text_fields = {
            "xdelta_path": self.ui.lineEditConfigRomPatcherxdeltaPath,
            "rompatcher_js_path": self.ui.lineEditConfigRomPatcherRomPatcherjsPath,
        }

        self.discord_text_fields = {
            "webhook_url": self.ui.lineEditConfigDiscordWebhookUrl,
        }

        self.all_romsearch_options = {
            "run_romdownloader": self.ui.checkBoxConfigRunRomDownloader,
            "run_rahasher": self.ui.checkBoxConfigRunRAHasher,
            "run_datparser": self.ui.checkBoxConfigRunDatParser,
            "run_dupeparser": self.ui.checkBoxConfigRunDupeParser,
            "run_romchooser": self.ui.checkBoxConfigRunRomChooser,
            "run_rommover": self.ui.checkBoxConfigRunRomMover,
            "run_rompatcher": self.ui.checkBoxConfigRunRomPatcher,
            "dry_run": self.ui.checkBoxConfigDryRun,
        }

        self.all_romdownloader_options = {
            "sync_all": self.ui.checkBoxConfigRomDownloaderSyncAll,
            "use_absolute_url": self.ui.checkBoxConfigRomDownloaderUseAbsoluteUrl,
            "dry_run": self.ui.checkBoxConfigRomDownloaderDryRun,
        }

        self.all_dupeparser_options = {
            # "use_dat": self.ui.checkBoxConfigDupeParserUseDat,
            "use_retool": self.ui.checkBoxConfigDupeParserUseRetool,
        }

        self.all_gamefinder_options = {
            "filter_dupes": self.ui.checkBoxConfigGameFinderFilterDupes,
        }

        self.all_romparser_options = {
            "use_dat": self.ui.checkBoxConfigRomParserUseDat,
            "use_retool": self.ui.checkBoxConfigRomParserUseRetool,
            "use_ra_hashes": self.ui.checkBoxConfigRomParserUseRAHashes,
            "use_filename": self.ui.checkBoxConfigRomParserUseFilename,
        }

        self.all_romchooser_options = {
            "use_best_version": self.ui.checkBoxConfigRomChooserUseBestVersion,
            "filter_regions": self.ui.checkBoxConfigRomChooserFilterRegions,
            "filter_languages": self.ui.checkBoxConfigRomChooserFilterLanguages,
            "dry_run": self.ui.checkBoxConfigRomChooserDryRun,
        }

        self.all_dat_filters = {
            "add-ons": self.ui.checkBoxConfigRomChooserDatFiltersAddons,
            "applications": self.ui.checkBoxConfigRomChooserDatFiltersApplications,
            "audio": self.ui.checkBoxConfigRomChooserDatFiltersAudio,
            "bad_dumps": self.ui.checkBoxConfigRomChooserDatFiltersBadDumps,
            "console": self.ui.checkBoxConfigRomChooserDatFiltersConsole,
            "bonus_discs": self.ui.checkBoxConfigRomChooserDatFiltersBonusDiscs,
            "coverdiscs": self.ui.checkBoxConfigRomChooserDatFiltersCoverdiscs,
            "demos": self.ui.checkBoxConfigRomChooserDatFiltersDemos,
            "educational": self.ui.checkBoxConfigRomChooserDatFiltersEducational,
            "games": self.ui.checkBoxConfigRomChooserDatFiltersGames,
            "manuals": self.ui.checkBoxConfigRomChooserDatFiltersManuals,
            "multimedia": self.ui.checkBoxConfigRomChooserDatFiltersMultimedia,
            "pirate": self.ui.checkBoxConfigRomChooserDatFiltersPirate,
            "preproduction": self.ui.checkBoxConfigRomChooserDatFiltersPreproduction,
            "promotional": self.ui.checkBoxConfigRomChooserDatFiltersPromotional,
            "unlicensed": self.ui.checkBoxConfigRomChooserDatFiltersUnlicensed,
            "video": self.ui.checkBoxConfigRomChooserDatFiltersVideo,
        }

        # If we have a saved config already, load it here
        self.saved_config_json_filename = "saved_config.json"
        if os.path.exists(self.saved_config_json_filename):
            self.logger.info(f"Loading in previously saved config")

            json = load_json(self.saved_config_json_filename)
            saved_filename = json["saved_config"]
            self.load_config(saved_filename)
            self.ui.lineEditConfigConfigFile.setText(saved_filename)

    def get_platforms_changed(self, item):
        """Update platforms on check

        Will update the dictionary, and add/remove items from the include/exclude table as appropriate
        """

        platform = item.text()

        checked_state = item.checkState()
        if checked_state == Qt.CheckState.Checked:
            self.add_include_exclude_tab(platform)
            self.platform_items[platform]["check_state"] = True
        else:
            self.remove_include_exclude_tab(platform)
            self.platform_items[platform]["check_state"] = False

    def remove_include_exclude_tab(self, platform):
        """Removes an include/exclude tab from the tab widget

        Args:
            platform: Platform to delete from the table
        """

        try:
            idx = self.ui.tabWidgetConfigIncludeExclude.indexOf(
                self.include_exclude_dict[platform]["tab"]
            )
        except KeyError:
            return False

        # Remove the entry from the dictionary as well
        del self.include_exclude_dict[platform]

        self.ui.tabWidgetConfigIncludeExclude.removeTab(idx)

        return True

    def add_include_exclude_tab(
        self,
        platform,
    ):
        """Add an include/exclude tab for a platform

        Args:
            platform (str): Platform to add the includes/excludes for
        """

        tab_config = QWidget()
        grid_layout = QGridLayout()
        hlayout = QHBoxLayout(tab_config)

        text_edit_include, include_layout = add_include_exclude_layout(
            tab_config, text=self.tr("Includes")
        )
        grid_layout.addLayout(include_layout, 0, 0, 1, 1)

        text_edit_exclude, exclude_layout = add_include_exclude_layout(
            tab_config, text=self.tr("Excludes")
        )
        grid_layout.addLayout(exclude_layout, 0, 2, 1, 1)

        # Middle sep
        include_exclude_sep = QFrame(tab_config)
        include_exclude_sep.setFrameShadow(QFrame.Shadow.Plain)
        include_exclude_sep.setFrameShape(QFrame.Shape.VLine)

        grid_layout.addWidget(include_exclude_sep, 0, 1, 1, 1)

        hlayout.addLayout(grid_layout)
        self.ui.tabWidgetConfigIncludeExclude.addTab(tab_config, platform)

        self.include_exclude_dict[platform] = {
            "tab": tab_config,
            "includes": text_edit_include,
            "excludes": text_edit_exclude,
        }

        return True

    def populate_list(
        self,
        default_config_key,
        list_widget,
        check_state=None,
    ):
        """Load items from a dict, potentially checked/unchecked"""

        item_dict = {}

        all_keys = self.default_config[default_config_key]

        for key in all_keys:
            item = add_item_to_list(
                list_widget,
                self.tr(key),
                check_state=check_state,
            )
            item_dict[key] = {
                "item": item,
                "check_state": check_state,
            }

        return item_dict

    def load_config_from_menu(self):
        """Load config from the menu item"""

        filename = self.get_config_name()
        self.load_config(filename)

    def get_config_name(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            caption=self.tr("Open config"),
            dir=os.getcwd(),
            filter=self.tr("Config file (*.yml;*.yaml)"),
        )
        self.ui.lineEditConfigConfigFile.setText(filename)

        return filename

    def load_config(
        self,
        filename,
    ):
        """Load config yaml from file"""

        # Only load if we actually have a filename
        if filename != "":
            self.config = load_yml(filename)

            # Start by setting lists, then checkboxes, then text fields, then any extraneous things left
            self.set_lists()
            self.set_checkboxes()
            self.set_text_fields()
            self.set_romsearch_method()
            self.set_logger_level()
            self.set_includes_excludes()

    def set_directory_name(
        self,
        line_edit,
    ):
        """Make a button set a directory name

        Args:
            line_edit (QLineEdit): The QLineEdit widget to set the text for
        """

        filename = QFileDialog.getExistingDirectory(
            self,
            caption=self.tr("Select directory"),
            dir=os.getcwd(),
        )
        if filename != "":
            line_edit.setText(filename)

    def set_file_name(
        self,
        line_edit,
    ):
        """Make a button set a file name

        Args:
            line_edit (QLineEdit): The QLineEdit widget to set the text for
        """

        filename, _ = QFileDialog.getOpenFileName(
            self,
            caption=self.tr("Select file"),
            dir=os.getcwd(),
        )
        if filename != "":
            line_edit.setText(filename)

    def set_lists(self):
        """Set the various lists across the config"""

        self.set_platforms()
        self.set_regions()
        self.set_languages()

    def set_platforms(self):
        """Set the platform list"""

        if "platforms" not in self.config:
            return False

        platforms = self.config["platforms"]
        set_ordered_list(
            self.ui.listWidgetConfigPlatforms,
            item_dict=self.platform_items,
            items=platforms,
        )

    def set_regions(self):
        """Set the regions list"""

        if "region_preferences" not in self.config:
            return False

        regions = self.config["region_preferences"]
        set_ordered_list(
            self.ui.listWidgetConfigRegionsLanguagesRegions,
            item_dict=self.region_items,
            items=regions,
        )

    def set_languages(self):
        """Set the language list"""

        if "language_preferences" not in self.config:
            return False

        languages = self.config["language_preferences"]
        set_ordered_list(
            self.ui.listWidgetConfigRegionsLanguagesLanguages,
            item_dict=self.language_items,
            items=languages,
        )

    def set_checkboxes(self):
        """Set checkboxes across the config"""

        keys = {
            "romsearch": self.all_romsearch_options,
            "romdownloader": self.all_romdownloader_options,
            "dupeparser": self.all_dupeparser_options,
            "gamefinder": self.all_gamefinder_options,
            "romparser": self.all_romparser_options,
            "romchooser": self.all_romchooser_options,
        }

        # Set all the various tabs
        for k in keys:
            self.set_generic_checkbox(k, keys[k])

        # Dat filters we do a bit differently
        self.set_dat_filter_checkboxes()

    def set_generic_checkbox(
        self,
        config_key,
        options,
    ):
        """Set checkboxes across generic tabs in the config"""

        if config_key not in self.config:
            return False

        for o in options:
            if o in self.config[config_key]:
                check_state = self.config[config_key][o]

                options[o].setChecked(check_state)

        return True

    def set_dat_filter_checkboxes(self):
        """Set the .dat filter checkboxes"""

        if "romchooser" not in self.config:
            return False

        # We also want to loop over the filter dats here, if they're not in the list set them False
        if "dat_filters" in self.config["romchooser"]:

            all_filters = self.config["romchooser"]["dat_filters"]
            if isinstance(all_filters, str):
                all_filters = [all_filters]

            for d in self.all_dat_filters:
                if d in all_filters:
                    self.all_dat_filters[d].setChecked(True)
                else:
                    self.all_dat_filters[d].setChecked(False)

        return True

    def set_text_fields(self):
        """Set checkboxes across the config"""

        keys = {
            "dirs": self.all_dirs,
            "romdownloader": self.romdownloader_text_fields,
            "rahasher": self.rahasher_text_fields,
            "rompatcher": self.rompatcher_text_fields,
            "discord": self.discord_text_fields,
        }

        for k in keys:
            self.set_generic_text_fields(k, keys[k])

    def set_generic_text_fields(
        self,
        config_key,
        text_fields,
    ):
        """Set generic text fields

        Args:
            config_key (str): The config key to set text fields for
            text_fields: Dictionary of the various text fields to set values for
        """

        if config_key not in self.config:
            self.config[config_key] = {}

        for d in text_fields:
            if d in self.config[config_key]:
                field_val = self.config[config_key][d]
                text_fields[d].setText(field_val)

    def set_romsearch_method(self):
        """Set the ROMSearch method from the config file"""

        if "romsearch" not in self.config:
            return False

        if "method" in self.config["romsearch"]:

            method = self.config["romsearch"]["method"]

            if method == "filter_then_download":
                button = self.ui.radioButtonConfigRomsearchMethodFilterDownload
            elif method == "download_then_filter":
                button = self.ui.radioButtonConfigRomsearchMethodDownloadFilter
            else:
                raise ValueError(f"Do not understand ROMSearch method {method}")

            button.setChecked(True)

        return True

    def set_logger_level(self):
        """Set the logger level from the config file"""

        if "logger" not in self.config:
            return False

        if "level" in self.config["logger"]:

            level = self.config["logger"]["level"]

            if level == "debug":
                button = self.ui.radioButtonConfigLoggerLevelDebug
            elif level == "info":
                button = self.ui.radioButtonConfigLoggerLevelInfo
            elif level == "critical":
                button = self.ui.radioButtonConfigLoggerLevelCritical
            else:
                raise ValueError(f"Do not understand logger level {level}")

            button.setChecked(True)

        return True

    def set_includes_excludes(self):
        """Set any includes/excludes config file"""

        mappings = {
            "include_games": "includes",
            "exclude_games": "excludes",
        }

        for m in mappings:
            if m in self.config:

                platforms = self.config[m]
                for p in platforms:
                    includes = "\n".join(self.config[m][p])

                    if p in self.include_exclude_dict:
                        self.include_exclude_dict[p][mappings[m]].setPlainText(includes)

        return True

    def create_file(self):
        """Get filename to save config file to"""

        filename, _ = QFileDialog.getSaveFileName(
            self,
            caption=self.tr("New config"),
            dir=os.getcwd(),
            filter=self.tr("Config file (*.yml)"),
        )
        self.ui.lineEditConfigConfigFile.setText(filename)

    def save_config(self):
        """Get config values and save to file"""

        # Get the filename
        filename = self.ui.lineEditConfigConfigFile.text()

        # Build up the dictionary
        self.config = {}

        # Get the config directories
        self.get_generic_text_value(
            "dirs",
            self.all_dirs,
        )

        # Platforms
        self.get_ordered_list(self.ui.listWidgetConfigPlatforms, "platforms")

        # Regions/languages
        self.get_ordered_list(
            self.ui.listWidgetConfigRegionsLanguagesRegions, "region_preferences"
        )
        self.get_ordered_list(
            self.ui.listWidgetConfigRegionsLanguagesLanguages, "language_preferences"
        )

        # Includes/Excludes
        self.get_include_excludes()

        keys = {
            "romsearch": self.all_romsearch_options,
            "romdownloader": self.all_romdownloader_options,
            "dupeparser": self.all_dupeparser_options,
            "gamefinder": self.all_gamefinder_options,
            "romparser": self.all_romparser_options,
            "romchooser": self.all_romchooser_options,
        }

        # Module options. Checkboxes first
        self.get_romsearch_method()
        for k in keys:
            self.get_generic_options(k, keys[k])

        # Then text fields
        keys = {
            "romdownloader": self.romdownloader_text_fields,
            "rahasher": self.rahasher_text_fields,
            "rompatcher": self.rompatcher_text_fields,
            "discord": self.discord_text_fields,
        }
        for k in keys:
            self.get_generic_text_value(k, keys[k])

        # Dat filters we do a bit differently
        self.get_dat_filters()

        # Finally, the logger level
        self.get_logger_level()

        # Save out the config file
        save_yml(filename, self.config)

        # Also save out this to somewhere accessible, so we know it exists
        json = {"saved_config": filename}
        save_json(json, self.saved_config_json_filename)

    def get_config_dirs(self):
        """Get directories from the main tab"""

        if "dirs" not in self.config:
            self.config["dirs"] = {}

        for d in self.all_dirs:
            dir_name = self.all_dirs[d].text()
            if dir_name != "":
                self.config["dirs"][d] = dir_name

    def get_generic_text_value(
        self,
        key,
        text_fields,
        add_at_top=True,
    ):
        """Get text fields generically

        Args:
            key (str): The config key to get text fields for
            text_fields (dict): Dictionary of the various text fields to get values for
            add_at_top (bool): If True, add the text fields at the top of the dictionary.
                Defaults to True
        """

        if key not in self.config:
            self.config[key] = {}

        config = {}

        for d in text_fields:
            text_val = text_fields[d].text()
            if text_val != "":
                config[d] = text_val

        if add_at_top:
            self.config[key] = {**config, **self.config[key]}
        else:
            self.config[key] = {**self.config[key], **config}

        # If the dictionary is empty, delete
        if len(self.config[key]) == 0:
            del self.config[key]

    def get_ordered_list(
        self,
        list_widget,
        key,
    ):
        """Get checked items from an ordered list"""

        n_items = list_widget.count()

        items = []

        for i in range(n_items):

            # Get item name, and check state
            item = list_widget.item(i)
            item_name = item.text()
            check_state = item.checkState()

            if check_state == Qt.CheckState.Checked:
                items.append(item_name)

        # Only add if we actually have some
        if len(items) > 0:
            self.config[key] = items

    def get_include_excludes(self):
        """Get includes/excludes from the list"""

        # Includes
        self.add_include_exclude_to_config(
            config_key="include_games",
            dict_key="includes",
        )
        self.add_include_exclude_to_config(
            config_key="exclude_games",
            dict_key="excludes",
        )

    def add_include_exclude_to_config(
        self,
        config_key,
        dict_key,
    ):
        """Add from the include/exclude text edit boxes to config

        Args:
            config_key (str): The key for the config dict
            dict_key (str): The key for the include/exclude dict
        """

        self.config[config_key] = {}

        for platform in self.include_exclude_dict:

            all_vals = self.include_exclude_dict[platform][dict_key].toPlainText()
            all_vals_list = all_vals.split("\n")

            # Loop over, find any potential blank entries
            blank_idx = []
            for i in all_vals_list:
                if i == "":
                    blank_idx.append(i)
            for idx in blank_idx[::-1]:
                all_vals_list.remove(idx)

            # Only add if we have something
            if len(all_vals_list) > 0:
                self.config[config_key][platform] = all_vals_list

        if len(self.config[config_key]) == 0:
            del self.config[config_key]

        return True

    def get_generic_options(
        self,
        key,
        options,
    ):
        """Get generic options from a config tab

        Args:
            key (str): The config key to get fields for
            options (dict): Dictionary of the various options to get values for
        """

        if key not in self.config:
            self.config[key] = {}

        for o in options:
            checked_state = options[o].isChecked()
            self.config[key][o] = checked_state

        # If the dictionary is empty, delete
        if len(self.config[key]) == 0:
            del self.config[key]

        return True

    def get_romsearch_method(self):
        """Get the ROMSearch method from the button config"""

        if "romsearch" not in self.config:
            self.config["romsearch"] = {}

        # Get the method from the radio button group
        romsearch_method_text = (
            self.ui.radioButtonConfigRomsearchMethod.checkedButton().text()
        )

        if romsearch_method_text == "Filter, then download":
            romsearch_method = "filter_then_download"
        elif romsearch_method_text == "Download, then filter":
            romsearch_method = "download_then_filter"
        else:
            raise ValueError(
                f"Do not understand ROMSearch method {romsearch_method_text}"
            )

        self.config["romsearch"]["method"] = romsearch_method

        return True

    def get_dat_filters(self):
        """Set the dat filters as a list"""

        if "romchooser" not in self.config:
            self.config["romchooser"] = {}

        # dat filters
        dat_filters = []
        for d in self.all_dat_filters:
            checked_state = self.all_dat_filters[d].isChecked()
            if checked_state:
                dat_filters.append(d)
        if len(dat_filters) > 0:
            self.config["romchooser"]["dat_filters"] = dat_filters

        return True

    def get_logger_level(self):
        """Get the logger level from the button config"""

        if "logger" not in self.config:
            self.config["logger"] = {}

        # Get the method from the radio button group
        logger_level = (
            self.ui.radioButtonConfigLoggerLevel.checkedButton().text().lower()
        )
        self.config["logger"]["level"] = logger_level

        return True
