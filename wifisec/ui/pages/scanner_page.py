"""Scan page: interface picker, scan button, results table, exports."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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

from wifisec.core import scanner
from wifisec.ui.workers import ScanWorker

COLUMNS = ["ESSID", "BSSID", "Ch", "Encryption", "Signal", "Q(%)", "Security"]


class ScannerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        layout = QVBoxLayout(self)

        title = QLabel("Scanner")
        title.setObjectName("page_title")
        layout.addWidget(title)

        top = QHBoxLayout()
        top.addWidget(QLabel("Interface:"))
        self.iface_box = QComboBox()
        top.addWidget(self.iface_box)
        self.refresh_btn = QPushButton("Refresh interfaces")
        self.refresh_btn.clicked.connect(self.refresh_interfaces)
        top.addWidget(self.refresh_btn)
        self.scan_btn = QPushButton("Scan")
        self.scan_btn.clicked.connect(self.start_scan)
        top.addWidget(self.scan_btn)
        top.addStretch()
        layout.addLayout(top)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        bottom = QHBoxLayout()
        csv_btn = QPushButton("Export CSV")
        csv_btn.clicked.connect(lambda: self.export("csv"))
        json_btn = QPushButton("Export JSON")
        json_btn.clicked.connect(lambda: self.export("json"))
        txt_btn = QPushButton("Export TXT report")
        txt_btn.clicked.connect(self.export_txt)
        bottom.addWidget(csv_btn)
        bottom.addWidget(json_btn)
        bottom.addWidget(txt_btn)
        bottom.addStretch()
        layout.addLayout(bottom)

        self.last_networks = []
        self.refresh_interfaces()

    def refresh_interfaces(self):
        self.iface_box.clear()
        for iface in scanner.get_wifi_interfaces():
            self.iface_box.addItem(iface)

    def start_scan(self):
        if self.worker and self.worker.isRunning():
            return
        iface = self.iface_box.currentText() or None
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("Scanning...")
        self.worker = ScanWorker(iface)
        self.worker.finished_ok.connect(self.on_results)
        self.worker.failed.connect(self.on_error)
        self.worker.finished.connect(self.on_done)
        self.worker.start()

    def on_results(self, networks):
        self.last_networks = networks
        self.table.setRowCount(0)
        for net in networks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, key in enumerate(["ESSID", "BSSID", "Channel",
                                       "Encryption", "Signal", "Quality(%)",
                                       "Security Level"]):
                item = QTableWidgetItem(str(net.get(key, "")))
                if col in (5, 6):
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
        self.table.resizeColumnsToContents()

    def on_error(self, tb):
        QMessageBox.critical(self, "Scan failed", tb)

    def on_done(self):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan")

    def export(self, kind):
        if not self.last_networks:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save results", "")
        if not path:
            return
        if kind == "csv":
            scanner.save_results_csv(self.last_networks, path)
        else:
            scanner.save_results_json(self.last_networks, path)

    def export_txt(self):
        if not self.last_networks:
            return
        scanner.export_report_txt(scanner.generate_report(self.last_networks))