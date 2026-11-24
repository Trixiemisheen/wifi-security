"""Overview page: platform, privileges, tool availability, capability matrix."""
import os
import subprocess
import sys

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wifisec.core.config import TOOL_NAME, TOOL_VERSION
from wifisec.core.scanner import IS_WINDOWS, get_wifi_interfaces
from wifisec.core.toolchain import (
    INSTALL_HINTS,
    LINUX_TOOLS,
    WINDOWS_TOOLS,
    ensure_tools_dir,
    tool_report,
)
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

        box = QGroupBox("System")
        self.form = QFormLayout(box)
        self.host_label = QLabel()
        self.admin_label = QLabel()
        self.mode_label = QLabel()
        self.mode_label.setWordWrap(True)
        self.form.addRow("Interfaces:", self.host_label)
        self.form.addRow("Admin/root:", self.admin_label)
        self.form.addRow("Mode:", self.mode_label)
        layout.addWidget(box)

        self.tools_box = QGroupBox("Capabilities")
        self.tools_layout = QFormLayout(self.tools_box)
        layout.addWidget(self.tools_box)

        buttons = QHBoxLayout()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        open_tools = QPushButton("Open tools folder")
        open_tools.clicked.connect(self.open_tools_folder)
        buttons.addWidget(refresh)
        buttons.addWidget(open_tools)
        buttons.addStretch()
        layout.addLayout(buttons)

        hint = QLabel(
            "Windows design: capture on Windows (netsh trace, experimental) or import "
            "captures from Linux/phone, then crack natively with hashcat (GPU) and "
            "auto-install the WLAN profile. Drop .exe builds into tools/ and they are "
            "detected automatically.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch()

        self.refresh()

    def refresh(self):
        ifaces = get_wifi_interfaces()
        self.host_label.setText(", ".join(ifaces) or "None found")
        self.admin_label.setText("Yes" if is_admin() else "No")
        if IS_WINDOWS:
            self.mode_label.setText(
                "Windows: scan, saved keys, open/stored-profile takeover, native "
                "GPU cracking, profile install + connect. Monitor-mode capture: "
                "experimental (passive only).")
        else:
            self.mode_label.setText("Linux: full capture + crack + connect pipeline.")

        while self.tools_layout.rowCount():
            self.tools_layout.removeRow(0)
        report = tool_report(WINDOWS_TOOLS if IS_WINDOWS else LINUX_TOOLS)
        for name, path in report.items():
            if path:
                lbl = QLabel(f"✔ {os.path.basename(path)}")
                lbl.setStyleSheet("color: #7de87d;")
                lbl.setToolTip(path)
            else:
                lbl = QLabel(f"✘ {name} — {INSTALL_HINTS.get(name, 'install it')}")
                lbl.setStyleSheet("color: #ff6b6b;")
            self.tools_layout.addRow(name, lbl)

    def open_tools_folder(self):
        path = ensure_tools_dir()
        try:
            if IS_WINDOWS:
                os.startfile(path)  # noqa: S606
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except OSError:
            pass