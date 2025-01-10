import os
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog

import romsearch
from .layout_about import Ui_About


class AboutWindow(QDialog):

    def __init__(self, parent=None):
        """ROMSearch About window"""

        super().__init__()

        self.ui = Ui_About()
        self.ui.setupUi(self)

        # Set the GUI icon
        icon_path = os.path.join(os.path.dirname(__file__), "img", "logo.png")
        icon = QPixmap(icon_path)
        self.ui.labelIcon.setPixmap(icon)

        # Set the version
        version = romsearch.__version__
        self.ui.aboutVersion.setText(f"v{version}")
