"""Main window: sidebar + stacked pages, theme, startup update check."""
from PySide6.QtWidgets import (
    QHBoxLayout, QMainWindow, QMessageBox, QStackedWidget, QWidget,
)

from wifisec.core.config import TOOL_NAME
from wifisec.services import settings as settings_service
from wifisec.ui.pages.dashboard import DashboardPage
from wifisec.ui.pages.password_page import PasswordPage
from wifisec.ui.pages.pentest_page import PentestPage
from wifisec.ui.pages.scanner_page import ScannerPage
from wifisec.ui.pages.settings_page import SettingsPage
from wifisec.ui.sidebar import PAGES, Sidebar
from wifisec.ui.theme import build_qss
from wifisec.ui.workers import UpdateWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{TOOL_NAME}")
        self.resize(1100, 700)

        self._settings = settings_service.load_settings()
        self._workers = []

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.pages = [
            DashboardPage(),
            ScannerPage(),
            PasswordPage(),
            PentestPage(),
            SettingsPage(self),
        ]
        for page in self.pages:
            self.stack.addWidget(page)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        self.apply_theme()
        self._start_update_check()

    def apply_theme(self):
        s = settings_service.load_settings()
        self.setStyleSheet(build_qss(s["theme"], s["density"]))

    def _start_update_check(self):
        if not self._settings.get("update_on_startup", True):
            return
        worker = UpdateWorker()
        worker.finished_ok.connect(self._on_update)
        self._workers.append(worker)
        worker.start()

    def _on_update(self, status):
        if status == "updated":
            QMessageBox.information(
                self, "Updates",
                "Updates were applied. Restart the app to use the new version.")

    def closeEvent(self, event):
        for w in self._workers:
            if w.isRunning():
                w.cancel()
        for page in self.pages:
            worker = getattr(page, "worker", None)
            if worker and worker.isRunning():
                worker.cancel()
        self._workers.clear()
        super().closeEvent(event)


def run() -> int:
    """Console-script entry point."""
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()