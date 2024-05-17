from PySide6.QtWidgets import QDialog

from .layout_about import Ui_About


class AboutWindow(QDialog):

    def __init__(self, parent=None):
        """ROMSearch About window"""

        super().__init__()

        self.ui = Ui_About()
        self.ui.setupUi(self)
