"""Overview page: status, tools, quick info."""
import shutil

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from wifisec.core.config import TOOL_NAME, TOOL_VERSION
from wifisec.core.scanner import get_wifi_interfaces, IS_WINDOWS
from wifisec.services.admin_check import is_admin, privilege_warning


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        title = QLabel(f"{TOOL_NAME} v{TOOL_VERSION}")
        title.setObjectName("page_title")
        layout.addWidget(title)

        self.warning = QLabel(privilege_warning())
        self.warning.setObjectName("banner")
        self.warning.setVisible(bool(privilege_warning()))
        layout.addWidget(self.warning)

        self.grid = QGridLayout()
        layout.addLayout(self.grid)
        self.info_labels = {}

        tools_row = QGridLayout()
        tools = ["airmon-ng", "airodump-ng", "aireplay-ng", "aircrack-ng",
                 "hcxdumptool", "hashcat"]
        self.tool_labels = {}
        for i, tool in enumerate(tools):
            lbl = QLabel()
            self.tool_labels[tool] = lbl
            tools_row.addWidget(lbl, i // 3, i % 3)
        layout.addLayout(tools_row)

        layout.addStretch()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        layout.addWidget(refresh)

        self.refresh()

    def refresh(self):
        ifaces = get_wifi_interfaces()
        rows = {
            "Interfaces": ", ".join(ifaces) or "None found",
            "Admin/root": "Yes" if is_admin() else "No",
            "Platform": "Windows" if IS_WINDOWS else "Linux/other",
            "Mode": "Full attack support (Linux)" if not IS_WINDOWS
                    else "Limited: open networks / stored profiles only",
        }
        for i, (key, value) in enumerate(rows.items()):
            k = self.info_labels.get(f"k{i}", QLabel(key))
            v = self.info_labels.get(f"v{i}", QLabel())
            v.setText(value)
            k.setStyleSheet("font-weight: bold;")
            self.grid.addWidget(k, i, 0)
            self.grid.addWidget(v, i, 1)
            self.info_labels[f"k{i}"] = k
            self.info_labels[f"v{i}"] = v

        for tool, lbl in self.tool_labels.items():
            found = shutil.which(tool) is not None
            lbl.setText(f"{'✔' if found else '✘'} {tool}")
            lbl.setStyleSheet(f"color: {'#7de87d' if found else '#ff6b6b'};")