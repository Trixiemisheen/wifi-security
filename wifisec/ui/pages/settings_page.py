"""Settings page."""
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wifisec.core.config import TOOL_VERSION
from wifisec.services import settings as settings_service
from wifisec.ui.theme import THEMES
from wifisec.ui.workers import UpdateWorker


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._window = parent
        layout = QVBoxLayout(self)

        title = QLabel(f"Settings — v{TOOL_VERSION}")
        title.setObjectName("page_title")
        layout.addWidget(title)

        form = QFormLayout()
        self.theme_box = QComboBox()
        self.theme_box.addItems(THEMES.keys())
        form.addRow("Theme:", self.theme_box)
        self.density_box = QComboBox()
        self.density_box.addItems(["comfortable", "compact"])
        form.addRow("Density:", self.density_box)
        self.updates_cb = QCheckBox("Check for updates on startup")
        form.addRow(self.updates_cb)
        layout.addLayout(form)

        save_btn = QPushButton("Save settings")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        update_btn = QPushButton("Check for updates now")
        update_btn.clicked.connect(self.check_updates)
        layout.addWidget(update_btn)

        layout.addStretch()
        self.load()

    def load(self):
        s = settings_service.load_settings()
        self.theme_box.setCurrentText(s["theme"])
        self.density_box.setCurrentText(s["density"])
        self.updates_cb.setChecked(s["update_on_startup"])

    def save(self):
        settings_service.save_settings({
            "theme": self.theme_box.currentText(),
            "density": self.density_box.currentText(),
            "update_on_startup": self.updates_cb.isChecked(),
        })
        if self._window and hasattr(self._window, "apply_theme"):
            self._window.apply_theme()
        QMessageBox.information(self, "Saved", "Settings saved.")

    def check_updates(self):
        if self.worker and self.worker.isRunning():
            return
        self.worker = UpdateWorker()
        self.worker.finished_ok.connect(self.on_update)
        self.worker.failed.connect(
            lambda tb: QMessageBox.critical(self, "Error", tb))
        self.worker.start()

    def on_update(self, status):
        if status == "updated":
            QMessageBox.information(
                self, "Updates", "Updates applied — restart the app to use them.")
        else:
            QMessageBox.information(self, "Updates", f"Status: {status}.")
