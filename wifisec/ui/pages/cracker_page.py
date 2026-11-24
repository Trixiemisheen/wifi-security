"""Cracker page: import captures, crack with hashcat, install & connect."""
import os

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from wifisec.core import cracker as cracker_core
from wifisec.core.capture_windows import capture_wireless, is_supported
from wifisec.core.config import PENTEST_CONFIG
from wifisec.core.toolchain import find_tool
from wifisec.ui.workers import Worker

COLUMNS = ["SSID", "Password", "Hash"]


class CrackerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        layout = QVBoxLayout(self)

        title = QLabel("Cracker (Windows-native)")
        title.setObjectName("page_title")
        layout.addWidget(title)

        hc = find_tool("hashcat")
        self.status = QLabel("hashcat: " + (hc or "not found — put hashcat.exe in tools/"))
        self.status.setObjectName("banner" if not hc else "")
        layout.addWidget(self.status)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Hash file:"))
        self.hash_edit = QLineEdit()
        self.hash_edit.setPlaceholderText(".22000 / .cap / .pcapng / .hccapx")
        row1.addWidget(self.hash_edit)
        pick_hash = QPushButton("...")
        pick_hash.setMaximumWidth(40)
        pick_hash.clicked.connect(self.pick_hash)
        row1.addWidget(pick_hash)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Wordlist:"))
        self.word_edit = QLineEdit(PENTEST_CONFIG["wordlist"])
        row2.addWidget(self.word_edit)
        pick_word = QPushButton("...")
        pick_word.setMaximumWidth(40)
        pick_word.clicked.connect(self.pick_wordlist)
        row2.addWidget(pick_word)
        row2.addWidget(QLabel("Mode:"))
        self.mode_box = QComboBox()
        self.mode_box.addItems(["22000", "22001"])
        row2.addWidget(self.mode_box)
        layout.addLayout(row2)

        buttons = QHBoxLayout()
        self.crack_btn = QPushButton("Crack")
        self.crack_btn.clicked.connect(self.start_crack)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel)
        self.capture_btn = QPushButton("Capture 30s (experimental)")
        self.capture_btn.setVisible(is_supported())
        self.capture_btn.clicked.connect(self.start_capture)
        for b in (self.crack_btn, self.cancel_btn, self.capture_btn):
            buttons.addWidget(b)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.connect_btn = QPushButton("Install profile & connect")
        self.connect_btn.clicked.connect(self.install_selected)
        layout.addWidget(self.connect_btn)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

    # ---- pickers ----
    def pick_hash(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select capture",
            filter="Captures (*.22000 *.cap *.pcapng *.hccapx);;All files (*)")
        if path:
            self.hash_edit.setText(path)

    def pick_wordlist(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select wordlist")
        if path:
            self.word_edit.setText(path)

    # ---- workers ----
    def _run(self, fn, done, *args):
        if self.worker and self.worker.isRunning():
            return
        self.crack_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.worker = Worker(fn, *args)
        self.worker.log_line.connect(self.output.appendPlainText)
        self.worker.finished_ok.connect(done)
        self.worker.failed.connect(lambda tb: self.output.appendPlainText(tb))
        self.worker.finished.connect(self._done_ui)
        self.worker.start()

    def _done_ui(self):
        self.crack_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def cancel(self):
        if self.worker:
            self.worker.cancel()
            self.output.appendPlainText("[!] Cancel requested...")

    def start_crack(self):
        hashfile = self.hash_edit.text().strip()
        if not hashfile:
            return

        def job():
            path = cracker_core.normalize_to_22000(
                hashfile, log_callback=lambda m: self.worker.log_line.emit(str(m)))
            if not path:
                raise RuntimeError("Could not normalize capture to 22000 format.")
            return cracker_core.crack(
                path, self.word_edit.text().strip(), int(self.mode_box.currentText()),
                log_callback=lambda m: self.worker.log_line.emit(str(m)),
                cancel_check=self.worker.cancel_check)

        self._run(job, self.on_results)

    def start_capture(self):
        def job():
            return capture_wireless(
                30, out_dir=os.path.dirname(self.hash_edit.text() or os.getcwd()),
                log_callback=lambda m: self.worker.log_line.emit(str(m)),
                cancel_check=self.worker.cancel_check)

        self._run(job, self.on_capture)

    # ---- results ----
    def on_capture(self, path):
        if path:
            self.hash_edit.setText(path)
            self.output.appendPlainText(f"[+] Capture -> {path}")

    def on_results(self, results):
        self.table.setRowCount(0)
        for r in results:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(r.get("ssid", "")))
            self.table.setItem(row, 1, QTableWidgetItem(r.get("password", "")))
            self.table.setItem(row, 2, QTableWidgetItem(r.get("hash", "")))

    def install_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        ssid = self.table.item(row, 0).text()
        psk = self.table.item(row, 1).text()
        ok = cracker_core.install_profile_and_connect(
            ssid, psk, log_callback=self.output.appendPlainText)
        if not ok:
            QMessageBox.warning(self, "Connect", "Profile could not be applied.")