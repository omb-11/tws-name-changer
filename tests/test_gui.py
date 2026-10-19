import os
import sys
from datetime import datetime, timezone
import pytest
from PySide6.QtWidgets import QApplication

from tws_name_changer.bluetooth.base import DeviceObservation, DiscoverySource, Transport
from tws_name_changer.bluetooth.discovery import ScanResult, SourceResult, _AnnotatedList
from tws_name_changer.services.rename_service import RenameService
from tws_name_changer.storage.settings import Settings
from tws_name_changer.ui.main_window import MainWindow, AboutDialog


@pytest.fixture(scope="session")
def qapp():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


class DummyBackend:
    async def scan(self, timeout_seconds: float = 8.0):
        return []


def test_main_window_initialization(qapp, tmp_path):
    backend = DummyBackend()
    rename_service = RenameService()
    settings = Settings(tmp_path / "settings.json")
    window = MainWindow(backend, rename_service, settings)

    assert window.windowTitle() == "TWS Name Changer — Windows 11 Diagnostics"
    assert window.scan_button.isEnabled()
    assert window.refresh_button.isEnabled()
    assert not window.progress_bar.isVisible()
    assert window.device_list.count() == 0


def test_main_window_show_devices(qapp, tmp_path):
    backend = DummyBackend()
    rename_service = RenameService()
    settings = Settings(tmp_path / "settings.json")
    window = MainWindow(backend, rename_service, settings)

    now = datetime.now(timezone.utc)
    dev1 = DeviceObservation(
        key="ble:112233445566",
        name="Earbuds BLE",
        address="112233445566",
        transport=Transport.BLE,
        rssi_dbm=-55,
        seen_at=now,
        source=DiscoverySource.BLE_ADVERTISEMENT,
    )
    dev2 = DeviceObservation(
        key="classic:4142FF85AA71",
        name="pTron TWS",
        address="4142FF85AA71",
        transport=Transport.CLASSIC,
        rssi_dbm=None,
        seen_at=now,
        source=DiscoverySource.WINDOWS_PAIRED_CLASSIC,
        paired=False,
    )

    scan_res = ScanResult(
        devices=[dev1, dev2],
        source_results=[
            SourceResult("BLE", observations=[dev1]),
            SourceResult("Windows paired Classic", observations=[dev2]),
        ],
    )
    annotated = _AnnotatedList([dev1, dev2], scan_res)

    window._show_devices(annotated)
    assert window.device_list.count() == 2
    assert "Earbuds BLE" in window.detail_name.text()
    assert "112233445566" in window.detail_address.text()
    assert "Live BLE" in window.detail_source.text()


def test_main_window_select_classic_device(qapp, tmp_path):
    backend = DummyBackend()
    rename_service = RenameService()
    settings = Settings(tmp_path / "settings.json")
    window = MainWindow(backend, rename_service, settings)

    now = datetime.now(timezone.utc)
    dev = DeviceObservation(
        key="classic:4142FF85AA71",
        name="pTron TWS",
        address="4142FF85AA71",
        transport=Transport.CLASSIC,
        rssi_dbm=None,
        seen_at=now,
        source=DiscoverySource.WINDOWS_PAIRED_CLASSIC,
        paired=False,
    )

    window._show_devices([dev])
    window.device_list.setCurrentRow(0)

    assert "pTron TWS" in window.detail_name.text()
    assert "4142FF85AA71" in window.detail_address.text()
    assert "Windows Paired" in window.detail_source.text()
    assert "Not paired" in window.detail_pairing.text()
    assert "Unsupported" in window.detail_rename_support.text()


def test_main_window_request_rename_no_selection(qapp, tmp_path):
    backend = DummyBackend()
    rename_service = RenameService()
    settings = Settings(tmp_path / "settings.json")
    window = MainWindow(backend, rename_service, settings)

    window._clear_details()
    window.device_list.setCurrentItem(None)
    window.request_rename()
    assert "Select a device" in window.status.text()


def test_about_dialog_initialization(qapp):
    dialog = AboutDialog()
    assert "About TWS Name Changer" in dialog.windowTitle()
