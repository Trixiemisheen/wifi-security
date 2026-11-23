"""Password viewer page."""
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from wifisec.core.password_auditor import export_to_csv
from wifisec.services.admin_check import privilege_warning
from wifisec.ui.workers import PasswordWorker

COLUMNS = ["#", "SSID", "Password"]


class PasswordPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        layout = QVBoxLayout(self)

        title = QLabel("Password Viewer")
        title.setObjectName("page_title")
        layout.addWidget(title)

        self.warning = QLabel(privilege_warning())
        self.warning.setObjectName("banner")
        self.warning.setVisible(bool(privilege_warning()))
        layout.addWidget(self.warning)

        top = QHBoxLayout()
        self.load_btn = QPushButton("Load profiles")
        self.load_btn.clicked.connect(lambda: self.load(reveal=False))
        self.reveal_btn = QPushButton("Load with passwords")
        self.reveal_btn.clicked.connect(lambda: self.load(reveal=True))
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.export)
        top.addWidget(self.load_btn)
        top.addWidget(self.reveal_btn)
        top.addWidget(self.export_btn)
        top.addStretch()
        layout.addLayout(top)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.profiles = []

    def load(self, reveal=False):
        if self.worker and self.worker.isRunning():
            return
        self.load_btn.setEnabled(False)
        self.reveal_btn.setEnabled(False)
        self.worker = PasswordWorker(reveal=reveal)
        self.worker.finished_ok.connect(self.on_results)
        self.worker.failed.connect(
            lambda tb: QMessageBox.critical(self, "Error", tb))
        self.worker.finished.connect(self.on_done)
        self.worker.start()

    def on_results(self, profiles):
        self.profiles = profiles
        self.table.setRowCount(0)
        for p in profiles:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(p["index"])))
            self.table.setItem(row, 1, QTableWidgetItem(p["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(p.get("password", "***")))

    def on_done(self):
        self.load_btn.setEnabled(True)
        self.reveal_btn.setEnabled(True)

    def export(self):
        if not self.profiles:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "wifi_profiles.csv")
        if path:
            export_to_csv(self.profiles, path)
