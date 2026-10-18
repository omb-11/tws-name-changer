"""Responsive UI for scanning and honest unsupported rename results."""
from __future__ import annotations
import asyncio
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QPushButton, QVBoxLayout, QWidget
from ..bluetooth.base import DeviceObservation
from ..bluetooth.device_info import capability_summary, display_name
from ..bluetooth.discovery import DiscoveryBackend
from ..services.rename_service import RenameService


class ScanThread(QThread):
    finished_scan = Signal(object)
    failed = Signal(str)
    def __init__(self, backend: DiscoveryBackend) -> None:
        super().__init__()
        self.backend = backend
    def run(self) -> None:
        try:
            self.finished_scan.emit(asyncio.run(self.backend.scan(8.0)))
        except Exception as error:
            self.failed.emit(f"Scan could not start: {error}")


class MainWindow(QMainWindow):
    def __init__(self, backend: DiscoveryBackend, rename_service: RenameService) -> None:
        super().__init__()
        self._backend, self._rename_service = backend, rename_service
        self._devices: list[DeviceObservation] = []
        self._thread: ScanThread | None = None
        self.setWindowTitle("TWS Name Changer")
        root, layout = QWidget(self), QVBoxLayout()
        layout.addWidget(QLabel("Nearby BLE devices (observed names are not firmware-name proof):"))
        self.device_list = QListWidget()
        layout.addWidget(self.device_list)
        controls = QHBoxLayout()
        self.scan_button = QPushButton("Scan nearby BLE devices")
        self.scan_button.clicked.connect(self.start_scan)
        controls.addWidget(self.scan_button)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Custom name (verified provider required)")
        controls.addWidget(self.name_input)
        self.rename_button = QPushButton("Check rename support")
        self.rename_button.clicked.connect(self.request_rename)
        controls.addWidget(self.rename_button)
        layout.addLayout(controls)
        self.status = QLabel("Ready. Unsupported devices will not receive a command.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        root.setLayout(layout)
        self.setCentralWidget(root)

    def start_scan(self) -> None:
        if self._thread and self._thread.isRunning(): return
        self.scan_button.setEnabled(False)
        self.status.setText("Scanning…")
        self._thread = ScanThread(self._backend)
        self._thread.finished_scan.connect(self._show_devices)
        self._thread.failed.connect(self.status.setText)
        self._thread.finished.connect(lambda: self.scan_button.setEnabled(True))
        self._thread.start()

    def _show_devices(self, devices: list[DeviceObservation]) -> None:
        self._devices = devices
        self.device_list.clear()
        for device in devices:
            item = QListWidgetItem(f"{display_name(device)} — {capability_summary(device)}")
            item.setData(256, device.key)
            self.device_list.addItem(item)
        self.status.setText(f"Found {len(devices)} BLE observation(s). Select one to check support.")

    def request_rename(self) -> None:
        item = self.device_list.currentItem()
        device = next((x for x in self._devices if item and x.key == item.data(256)), None)
        if device is None:
            self.status.setText("Select a device first.")
            return
        result = asyncio.run(self._rename_service.request_rename(device, self.name_input.text()))
        self.status.setText(result.message)
