"""Responsive, modern PySide6 UI for Bluetooth discovery and honest rename diagnostics."""
from __future__ import annotations

import asyncio
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ..bluetooth.base import DeviceObservation, DiscoverySource, Transport
from ..bluetooth.device_info import capability_summary, display_name
from ..bluetooth.discovery import DiscoveryBackend, ScanResult, _AnnotatedList
from ..services.rename_service import RenameService
from ..storage.settings import Settings


class ScanThread(QThread):
    finished_scan = Signal(object)
    failed = Signal(str)

    def __init__(self, backend: DiscoveryBackend, timeout: float = 8.0) -> None:
        super().__init__()
        self.backend = backend
        self.timeout = timeout

    def run(self) -> None:
        try:
            results = asyncio.run(self.backend.scan(self.timeout))
            self.finished_scan.emit(results)
        except Exception as error:
            self.failed.emit(f"Scan failed: {error}")


class AboutDialog(QDialog):
    """Informative help and technical transparency dialog."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("About TWS Name Changer & Troubleshooting")
        self.resize(600, 480)

        layout = QVBoxLayout(self)

        title = QLabel("<h2>TWS Name Changer</h2>")
        layout.addWidget(title)

        text = QLabel(
            "<b>Overview:</b><br>"
            "TWS Name Changer is an honest diagnostic and discovery tool for Bluetooth "
            "earbuds on Windows 11. It discovers live BLE advertisements and reads "
            "Windows paired Bluetooth records without claiming unverified capabilities.<br><br>"
            "<b>Firmware Renaming vs. Local Windows Aliases:</b><br>"
            "• <i>Windows Display Alias:</i> Changing a device name in Windows Settings only updates "
            "a local registry entry on this specific PC. It does NOT change what the earbuds broadcast.<br>"
            "• <i>Genuine Firmware Renaming:</i> TWS earbuds (such as pTron, Boat, Noise, and generic JL/Actions "
            "chipsets) store their broadcast name in internal NVRAM/flash. Modifying this broadcast name "
            "requires proprietary vendor-specific OTA commands or companion apps. Universal or arbitrary "
            "Bluetooth writes risk bricking the hardware, so unverified devices remain strictly unsupported.<br><br>"
            "<b>Discovery Transports:</b><br>"
            "• <i>Live BLE Advertisements:</i> Directly detected radio packets broadcast by nearby devices right now.<br>"
            "• <i>Windows Paired Classic:</i> Cached system entries from the Windows Bluetooth device registry. "
            "These records exist even when the earbuds are powered off or miles away.<br><br>"
            "<b>Windows Bluetooth Error Reference:</b><br>"
            "• <b>0x800710DF (ERROR_DEVICE_NOT_AVAILABLE):</b> The Bluetooth adapter is turned off, or the "
            "Bluetooth driver/service needs to be restarted in Windows Settings.<br>"
            "• <b>0x80070005 (E_ACCESSDENIED):</b> Windows Privacy & Security &gt; Bluetooth &gt; 'Let apps "
            "access Bluetooth' is disabled. (Administrator privileges are NOT required)."
        )
        text.setWordWrap(True)
        text.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)


class MainWindow(QMainWindow):
    def __init__(
        self,
        backend: DiscoveryBackend,
        rename_service: RenameService,
        settings: Settings | None = None,
    ) -> None:
        super().__init__()
        self._backend = backend
        self._rename_service = rename_service
        self._settings = settings or Settings()
        self._devices: list[DeviceObservation] = []
        self._thread: ScanThread | None = None

        self.setWindowTitle("TWS Name Changer — Windows 11 Diagnostics")
        self.resize(850, 620)
        self._init_ui()

    def _init_ui(self) -> None:
        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(10)

        # Header bar
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        title_label = QLabel("<b>TWS Name Changer</b> — Bluetooth Diagnostics")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        subtitle_label = QLabel(
            "Discover nearby BLE advertisements and Windows paired records. "
            "Firmware renaming requires verified hardware protocols."
        )
        subtitle_label.setStyleSheet("color: #666; font-size: 12px;")
        header_text.addWidget(title_label)
        header_text.addWidget(subtitle_label)
        header_layout.addLayout(header_text)
        header_layout.addStretch()

        self.about_button = QPushButton("About & Help")
        self.about_button.clicked.connect(self.show_about)
        header_layout.addWidget(self.about_button)
        root_layout.addLayout(header_layout)

        # Action / Control bar
        control_bar = QHBoxLayout()
        self.scan_button = QPushButton("🔍 Scan Bluetooth Devices")
        self.scan_button.setStyleSheet("font-weight: bold; padding: 6px 14px;")
        self.scan_button.clicked.connect(self.start_scan)
        control_bar.addWidget(self.scan_button)

        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.start_scan)
        control_bar.addWidget(self.refresh_button)

        control_bar.addStretch()
        root_layout.addLayout(control_bar)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate marquee
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        root_layout.addWidget(self.progress_bar)

        # Main splitter (Device list on left, details on right)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left pane: Device List
        left_group = QGroupBox("Discovered Bluetooth Devices")
        left_layout = QVBoxLayout(left_group)
        self.device_list = QListWidget()
        self.device_list.currentItemChanged.connect(self._on_device_selected)
        left_layout.addWidget(self.device_list)
        splitter.addWidget(left_group)

        # Right pane: Details & Rename Actions
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Selected Device Details Box
        self.details_group = QGroupBox("Selected Device Details")
        details_form = QFormLayout(self.details_group)
        details_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.detail_name = QLabel("None selected")
        self.detail_name.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_form.addRow("<b>Name:</b>", self.detail_name)

        self.detail_address = QLabel("—")
        self.detail_address.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_form.addRow("<b>Address:</b>", self.detail_address)

        self.detail_source = QLabel("—")
        self.detail_source.setWordWrap(True)
        details_form.addRow("<b>Discovery Source:</b>", self.detail_source)

        self.detail_pairing = QLabel("—")
        details_form.addRow("<b>Windows Pairing:</b>", self.detail_pairing)

        self.detail_rssi = QLabel("—")
        details_form.addRow("<b>Signal (RSSI):</b>", self.detail_rssi)

        self.detail_services = QLabel("—")
        self.detail_services.setWordWrap(True)
        details_form.addRow("<b>Services:</b>", self.detail_services)

        self.detail_rename_support = QLabel("—")
        self.detail_rename_support.setWordWrap(True)
        details_form.addRow("<b>Rename Support:</b>", self.detail_rename_support)

        right_layout.addWidget(self.details_group)

        # Rename Action Box
        rename_group = QGroupBox("Firmware Rename Verification")
        rename_layout = QVBoxLayout(rename_group)
        rename_form = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter custom name to test support...")
        rename_form.addWidget(self.name_input)

        self.rename_button = QPushButton("Check / Attempt Rename")
        self.rename_button.clicked.connect(self.request_rename)
        rename_form.addWidget(self.rename_button)
        rename_layout.addLayout(rename_form)

        rename_note = QLabel(
            "<small><i>Note: Modifying local Windows display aliases does NOT change the name "
            "broadcast to phones or other laptops. Genuine firmware renaming requires verified "
            "vendor protocols.</i></small>"
        )
        rename_note.setWordWrap(True)
        rename_layout.addWidget(rename_note)
        right_layout.addWidget(rename_group)

        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 5)
        root_layout.addWidget(splitter, stretch=1)

        # Status / Feedback area
        self.status = QLabel("Ready. Click 'Scan Bluetooth Devices' to begin.")
        self.status.setWordWrap(True)
        self.status.setStyleSheet("padding: 6px; background: #f0f0f0; border-radius: 4px;")
        root_layout.addWidget(self.status)

        self.setCentralWidget(root)

    def show_about(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    def start_scan(self) -> None:
        if self._thread and self._thread.isRunning():
            return
        self.scan_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.progress_bar.show()
        self.status.setText("Scanning nearby BLE advertisements and Windows paired records…")

        self._thread = ScanThread(self._backend, timeout=8.0)
        self._thread.finished_scan.connect(self._show_devices)
        self._thread.failed.connect(self._show_scan_error)
        self._thread.finished.connect(self._on_scan_finished)
        self._thread.start()

    def _on_scan_finished(self) -> None:
        self.scan_button.setEnabled(True)
        self.refresh_button.setEnabled(True)
        self.progress_bar.hide()

    def _show_devices(self, devices: list[DeviceObservation]) -> None:
        self._devices = list(devices)
        self.device_list.clear()

        for device in devices:
            source_badge = "[BLE Live]" if device.source == DiscoverySource.BLE_ADVERTISEMENT else "[Windows Paired]"
            item_text = f"{display_name(device)}  {source_badge}\n  ↳ {device.address or 'No address'} · {capability_summary(device)}"
            item = QListWidgetItem(item_text)
            item.setData(256, device.key)
            self.device_list.addItem(item)

        count = len(self._devices)
        if isinstance(devices, _AnnotatedList) and devices.scan_result is not None:
            scan_result: ScanResult = devices.scan_result
            summary = scan_result.status_summary()
            if scan_result.all_failed:
                self.status.setText(f"No devices found — all discovery sources failed.\n{summary}")
            elif any(not r.succeeded for r in scan_result.source_results):
                self.status.setText(
                    f"Found {count} Bluetooth device observation(s) (partial discovery — some sources failed):\n{summary}"
                )
            else:
                self.status.setText(f"Found {count} Bluetooth observation(s) across all sources.\n{summary}")
        else:
            self.status.setText(f"Found {count} Bluetooth observation(s). Select a device to view details.")

        if count > 0:
            self.device_list.setCurrentRow(0)
        else:
            self._clear_details()

    def _clear_details(self) -> None:
        self.detail_name.setText("None selected")
        self.detail_address.setText("—")
        self.detail_source.setText("—")
        self.detail_pairing.setText("—")
        self.detail_rssi.setText("—")
        self.detail_services.setText("—")
        self.detail_rename_support.setText("—")

    def _on_device_selected(self, current: QListWidgetItem | None, previous: QListWidgetItem | None = None) -> None:
        if current is None:
            self._clear_details()
            return
        key = current.data(256)
        device = next((x for x in self._devices if x.key == key), None)
        if device is None:
            self._clear_details()
            return

        self.detail_name.setText(display_name(device))
        self.detail_address.setText(device.address or "Address not reported")

        if device.source == DiscoverySource.BLE_ADVERTISEMENT:
            self.detail_source.setText("🟢 Live BLE Advertisement (broadcasting nearby right now)")
        else:
            self.detail_source.setText(
                "🟡 Windows Paired Bluetooth Record (cached system record; does NOT prove device is nearby or connected)"
            )

        if device.paired is True:
            self.detail_pairing.setText("Paired (in Windows registry)")
        elif device.paired is False:
            self.detail_pairing.setText("Not paired (stored in Windows AEP device cache)")
        else:
            self.detail_pairing.setText("Not reported")

        if device.rssi_dbm is not None:
            self.detail_rssi.setText(f"{device.rssi_dbm} dBm")
        else:
            self.detail_rssi.setText("N/A (cached record, no live signal strength)")

        if device.service_uuids:
            self.detail_services.setText(f"{len(device.service_uuids)} UUID(s): " + ", ".join(device.service_uuids[:3]))
        else:
            self.detail_services.setText("None advertised")

        self.detail_rename_support.setText(
            "❌ Unsupported (No verified firmware protocol for this earbud model. Remote advertised name cannot be safely changed.)"
        )

    def _show_scan_error(self, message: str) -> None:
        self.status.setText(message)

    def request_rename(self) -> None:
        item = self.device_list.currentItem()
        if item is None:
            self.status.setText("Select a device from the list first.")
            return
        key = item.data(256)
        device = next((x for x in self._devices if x.key == key), None)
        if device is None:
            self.status.setText("Selected device could not be found.")
            return

        new_name = self.name_input.text()
        result = asyncio.run(self._rename_service.request_rename(device, new_name))
        self.status.setText(f"Rename Result: {result.message}")
        if result.status.value != "unsupported":
            QMessageBox.information(self, "Rename Result", result.message)
        else:
            QMessageBox.warning(
                self,
                "Firmware Renaming Unsupported",
                f"{result.message}\n\n"
                "Explanation: Generic TWS earbuds broadcast a name hardcoded in firmware/NVRAM. "
                "Writing a local Windows display alias does NOT change what other devices observe.",
            )
