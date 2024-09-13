import logging
import sys

import colorlog
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QListWidgetItem


@Slot()
def open_url(url):
    """Opens a URL"""

    QDesktopServices.openUrl(url)


def add_item_to_list(item_list, item_name, check_state=None):
    """Add item to list widget, optionally setting a check state

    Args:
        item_list (QListWidgetItem): Item to add
        item_name (str): Item name
        check_state (None, True, False): If None, will not set check
            state. Otherwise, will set checked (True) or not checked
            (False). Defaults to None
    """

    item = QListWidgetItem(item_list)
    item.setText(item_name)
    if check_state is not None:
        if not check_state:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)

    return item


def get_gui_logger(log_level="info"):
    logger = logging.getLogger()

    # Set the log level based on the provided parameter
    log_level = log_level.upper()
    if log_level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif log_level == "INFO":
        logger.setLevel(logging.INFO)
    elif log_level == "CRITICAL":
        logger.setLevel(logging.CRITICAL)
    else:
        logger.critical(f"Invalid log level '{log_level}', defaulting to 'INFO'")
        logger.setLevel(logging.INFO)
    log_handler = colorlog.StreamHandler(sys.stdout)
    log_handler.setFormatter(
        colorlog.ColoredFormatter("%(log_color)s%(levelname)s: %(message)s")
    )
    logger.addHandler(log_handler)

    return logger
