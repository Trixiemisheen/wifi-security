"""Navigation sidebar."""
from PySide6.QtWidgets import QListWidget, QListWidgetItem

PAGES = [
    ("Dashboard", "Ctrl+1"),
    ("Scanner", "Ctrl+2"),
    ("Password Viewer", "Ctrl+3"),
    ("Pentest", "Ctrl+4"),
    ("Cracker", "Ctrl+5"),
    ("Settings", "Ctrl+6"),
]


class Sidebar(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        for name, _shortcut in PAGES:
            QListWidgetItem(name, self)
        self.currentRowChanged.connect(self._noop)

    @staticmethod
    def _noop(_):
        pass
