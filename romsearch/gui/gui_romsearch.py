import os
from PySide6.QtCore import Slot, Signal, QObject, QThread, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
)

from romsearch import ROMSearch
from .gui_about import AboutWindow
from .gui_config import ConfigWindow
from .gui_utils import open_url, get_gui_logger
from .layout_romsearch import Ui_RomSearch


@Slot()
def close_all():
    """Close the application"""

    QApplication.closeAllWindows()


class MainWindow(QMainWindow):

    def __init__(self):
        """ROMSearch Main Window"""

        super().__init__()

        self.ui = Ui_RomSearch()
        self.ui.setupUi(self)

        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), "img", "logo.png")
        icon = QIcon()
        icon.addFile(icon_path, QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)

        log_level = self.ui.radioButtonConfigLoggerLevel.checkedButton().text().lower()
        self.logger = get_gui_logger(log_level=log_level)
        self.logger.warning("Do not close this window!")

        # Set up the worker threads for later
        self.romsearch_thread = None
        self.romsearch_worker = None

        # Set up the config file here
        self.config_window = ConfigWindow(self.ui, logger=self.logger)

        # File menu buttons
        new_config = self.ui.actionNewConfigFile
        new_config.triggered.connect(self.config_window.create_file)

        load_config = self.ui.actionLoadConfigFile
        load_config.triggered.connect(self.config_window.load_config_from_menu)

        save_config = self.ui.actionSaveConfigFile
        save_config.triggered.connect(self.config_window.save_config)

        exit_button = self.ui.actionExit
        exit_button.triggered.connect(close_all)

        # Help menu buttons
        documentation = self.ui.actionDocumentation
        documentation.triggered.connect(
            lambda: open_url("https://romsearch.readthedocs.io")
        )

        issues = self.ui.actionIssues
        issues.triggered.connect(
            lambda: open_url("https://github.com/bbtufty/romsearch/issues")
        )

        about = self.ui.actionAbout
        about.triggered.connect(lambda: AboutWindow(self).exec())

        # Main window buttons
        run_romsearch = self.ui.pushButtonRunRomsearch
        run_romsearch.clicked.connect(self.run_romsearch)

        exit_button = self.ui.pushButtonExit
        exit_button.clicked.connect(close_all)

    @Slot()
    def run_romsearch(self):
        """Run ROMSearch given the config file"""

        # Save out the config so we know we're good
        self.config_window.save_config()

        config_file = self.ui.lineEditConfigConfigFile.text()

        # Set up a thread so the UI doesn't hang
        self.romsearch_thread = QThread()
        self.romsearch_worker = RomSearchWorker(config_file=config_file)

        self.romsearch_worker.moveToThread(self.romsearch_thread)
        self.romsearch_thread.started.connect(self.romsearch_worker.run)

        # Delete the thread once we're done
        self.romsearch_worker.finished.connect(self.romsearch_thread.quit)
        self.romsearch_worker.finished.connect(self.romsearch_worker.deleteLater)
        self.romsearch_thread.finished.connect(self.romsearch_thread.deleteLater)

        # When finished, re-enable the UI
        self.romsearch_thread.finished.connect(
            lambda: self.ui.centralwidget.setEnabled(True)
        )
        # Start the thread
        self.romsearch_thread.start()

        # Disable the UI
        self.ui.centralwidget.setEnabled(False)


class RomSearchWorker(QObject):
    finished = Signal()

    def __init__(self, config_file):
        super().__init__()

        self.config_file = config_file

    def run(self):

        rs = ROMSearch(self.config_file)
        rs.run()

        self.finished.emit()
