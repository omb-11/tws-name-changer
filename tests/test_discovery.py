"""Tests for BLE and Windows paired-Classic discovery logic.

All tests are mocked; no Bluetooth hardware is required.
Hardware results are documented separately in reviews/M2_CODE_AUDIT.md.
"""
import asyncio
import sys
from datetime import timedelta
from types import SimpleNamespace

import pytest

from tws_name_changer.bluetooth.base import DiscoverySource, DeviceObservation, Transport
from tws_name_changer.bluetooth.discovery import (
    BleakDiscoveryBackend,
    DiscoveryError,
    ScanResult,
    SourceResult,
    UnifiedDiscoveryBackend,
    WindowsPairedClassicBackend,
    _AnnotatedList,
    _ble_adapter_message,
    _classic_adapter_message,
    _clean_name,
    merge_observations,
)
from tws_name_changer.bluetooth.device_info import display_name


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class FakeBackend:
    """In-test backend that either returns a device list or raises an exception."""

    def __init__(self, result: object) -> None:
        self.result = result

    async def scan(self, timeout_seconds: float) -> list[DeviceObservation]:
        if isinstance(self.result, Exception):
            raise self.result
        return self.result  # type: ignore[return-value]


def _ble_device(address: str = "AA:BB", name: str = "Example Buds", dt_offset: float = 0) -> DeviceObservation:
    from datetime import datetime, timezone
    return DeviceObservation(
        f"ble:{address}", name, address, Transport.BLE, -60,
        datetime.now(timezone.utc) + timedelta(seconds=dt_offset),
    )


def _classic_device(
    address: str | None = None,
    name: str = "Classic Buds",
    paired_id: str = "paired:one",
) -> DeviceObservation:
    from datetime import datetime, timezone
    key = f"classic:{address}" if address else paired_id
    return DeviceObservation(
        key, name, address, Transport.CLASSIC, None,
        datetime.now(timezone.utc),
        source=DiscoverySource.WINDOWS_PAIRED_CLASSIC, paired=True,
    )


# ---------------------------------------------------------------------------
# _clean_name
# ---------------------------------------------------------------------------

def test_clean_name_removes_control_characters():
    assert _clean_name(" Bud\x00s\n ") == "Buds"


def test_clean_name_missing_is_missing():
    assert _clean_name(None) is None


def test_clean_name_empty_string_is_none():
    assert _clean_name("   ") is None


def test_clean_name_truncates_to_248_characters():
    assert _clean_name("x" * 300) == "x" * 248


# ---------------------------------------------------------------------------
# display_name
# ---------------------------------------------------------------------------

def test_display_name_for_missing_name(device: DeviceObservation):
    nameless = DeviceObservation(
        device.key, None, device.address, device.transport,
        device.rssi_dbm, device.seen_at,
    )
    assert display_name(nameless) == "Unnamed Bluetooth device"


def test_display_name_returns_stripped_name(device: DeviceObservation):
    assert display_name(device) == "Example Buds"


# ---------------------------------------------------------------------------
# BLE adapter error messages
# ---------------------------------------------------------------------------

def test_known_windows_ble_hresult_has_specific_diagnosis():
    error = OSError("device not ready")
    error.winerror = -2147020577  # type: ignore[attr-defined]
    msg = _ble_adapter_message(error)
    assert "0x800710DF" in msg
    assert "Bluetooth is turned off" in msg
    assert "Device Manager" in msg


def test_ble_adapter_generic_oserror_gives_fallback_message():
    error = OSError("some other error")
    msg = _ble_adapter_message(error)
    assert "unavailable or not ready" in msg
    assert "0x800710DF" not in msg


# ---------------------------------------------------------------------------
# Classic adapter error messages
# ---------------------------------------------------------------------------

def test_classic_access_denied_winerror_gives_actionable_message():
    error = OSError("access denied")
    error.winerror = -2147024891  # type: ignore[attr-defined]  # 0x80070005
    msg = _classic_adapter_message(error)
    assert "0x80070005" in msg
    assert "Privacy & security" in msg
    assert "Administrator privileges are not required" in msg


def test_classic_permission_error_gives_actionable_message():
    error = PermissionError("access denied")
    msg = _classic_adapter_message(error)
    assert "0x80070005" in msg


def test_classic_generic_oserror_gives_fallback_message():
    error = OSError("adapter gone")
    msg = _classic_adapter_message(error)
    assert "adapter is unavailable" in msg
    assert "0x80070005" not in msg


# ---------------------------------------------------------------------------
# BleakDiscoveryBackend (mocked)
# ---------------------------------------------------------------------------

def test_ble_adapter_os_error_becomes_actionable(monkeypatch: pytest.MonkeyPatch):
    class Scanner:
        @classmethod
        async def discover(cls, **kwargs):  # noqa: ANN201
            raise OSError("not ready")

    monkeypatch.setitem(sys.modules, "bleak", SimpleNamespace(BleakScanner=Scanner))
    with pytest.raises(DiscoveryError, match="adapter is unavailable or not ready"):
        asyncio.run(BleakDiscoveryBackend().scan(1))


def test_ble_backend_negative_timeout_raises():
    with pytest.raises(ValueError, match="positive"):
        asyncio.run(BleakDiscoveryBackend().scan(-1))


# ---------------------------------------------------------------------------
# WindowsPairedClassicBackend (mocked)
# ---------------------------------------------------------------------------

def test_windows_paired_backend_labels_mocked_classic_record():
    class BluetoothDevice:
        @staticmethod
        def get_device_selector() -> str:
            return "selector"

        @staticmethod
        async def from_id_async(device_id: str) -> SimpleNamespace:
            return SimpleNamespace(bluetooth_address=0xAABBCCDDEEFF)

    class DeviceInformation:
        @staticmethod
        async def find_all_async_aqs_filter(selector: str) -> list:
            return [SimpleNamespace(id="device-id", name="Classic Buds", pairing=SimpleNamespace(is_paired=True))]

    backend = WindowsPairedClassicBackend(lambda: (BluetoothDevice, DeviceInformation))
    result = asyncio.run(backend.scan(1))
    assert result[0].source is DiscoverySource.WINDOWS_PAIRED_CLASSIC
    assert result[0].transport is Transport.CLASSIC
    assert result[0].address == "AABBCCDDEEFF"


def test_windows_paired_backend_oserror_access_denied_raises_discovery_error():
    """OSError with winerror -2147024891 must become a DiscoveryError with actionable text."""
    class BluetoothDevice:
        @staticmethod
        def get_device_selector() -> str:
            return "selector"

    class DeviceInformation:
        @staticmethod
        async def find_all_async_aqs_filter(selector: str):
            err = OSError("access denied")
            err.winerror = -2147024891  # type: ignore[attr-defined]
            raise err

    backend = WindowsPairedClassicBackend(lambda: (BluetoothDevice, DeviceInformation))
    with pytest.raises(DiscoveryError, match="0x80070005"):
        asyncio.run(backend.scan(1))


def test_windows_paired_backend_permission_error_raises_discovery_error():
    class BluetoothDevice:
        @staticmethod
        def get_device_selector() -> str:
            return "selector"

    class DeviceInformation:
        @staticmethod
        async def find_all_async_aqs_filter(selector: str):
            raise PermissionError("access denied")

    backend = WindowsPairedClassicBackend(lambda: (BluetoothDevice, DeviceInformation))
    with pytest.raises(DiscoveryError, match="0x80070005"):
        asyncio.run(backend.scan(1))


def test_windows_paired_backend_import_error_raises_discovery_error():
    def bad_loader():
        raise ImportError("winrt not installed")

    backend = WindowsPairedClassicBackend(bad_loader)
    with pytest.raises(DiscoveryError, match="not installed"):
        asyncio.run(backend.scan(1))


def test_windows_paired_backend_negative_timeout_raises():
    backend = WindowsPairedClassicBackend(lambda: (object(), object()))
    with pytest.raises(ValueError, match="positive"):
        asyncio.run(backend.scan(-1))


# ---------------------------------------------------------------------------
# merge_observations
# ---------------------------------------------------------------------------

def test_merge_uses_exact_address_not_name(device: DeviceObservation):
    classic = DeviceObservation(
        "classic:AA:BB", "Different display name", "AA:BB", Transport.CLASSIC, None,
        device.seen_at + timedelta(seconds=1), source=DiscoverySource.WINDOWS_PAIRED_CLASSIC,
    )
    # Same address → newer observation wins; different name is irrelevant.
    assert merge_observations([device, classic]) == [classic]


def test_merge_keeps_devices_with_different_addresses(device: DeviceObservation):
    other = DeviceObservation(
        "ble:CC:DD", "Other Buds", "CC:DD", Transport.BLE, -70, device.seen_at,
    )
    result = merge_observations([device, other])
    assert len(result) == 2


def test_merge_deduplicates_by_key_when_no_address():
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    a = DeviceObservation("paired:xyz", "Nameless", None, Transport.CLASSIC, None, now)
    b = DeviceObservation("paired:xyz", "Nameless", None, Transport.CLASSIC, None, now + timedelta(seconds=1))
    result = merge_observations([a, b])
    assert len(result) == 1
    assert result[0].seen_at == b.seen_at  # newer wins


def test_merge_empty_list_returns_empty():
    assert merge_observations([]) == []


def test_merge_single_device_unchanged(device: DeviceObservation):
    assert merge_observations([device]) == [device]


# ---------------------------------------------------------------------------
# UnifiedDiscoveryBackend — both sources succeed
# ---------------------------------------------------------------------------

def test_unified_list_keeps_ble_and_paired_classic_sources(device: DeviceObservation):
    classic = _classic_device(name="Example Buds")
    result = asyncio.run(
        UnifiedDiscoveryBackend(FakeBackend([device]), FakeBackend([classic])).scan(1)
    )
    assert {item.source for item in result} == {
        DiscoverySource.BLE_ADVERTISEMENT,
        DiscoverySource.WINDOWS_PAIRED_CLASSIC,
    }


def test_unified_annotates_result_with_scan_result(device: DeviceObservation):
    result = asyncio.run(
        UnifiedDiscoveryBackend(FakeBackend([device]), FakeBackend([])).scan(1)
    )
    assert isinstance(result, _AnnotatedList)
    assert isinstance(result.scan_result, ScanResult)


def test_unified_both_succeed_scan_result_marks_no_failures(device: DeviceObservation):
    classic = _classic_device()
    result = asyncio.run(
        UnifiedDiscoveryBackend(FakeBackend([device]), FakeBackend([classic])).scan(1)
    )
    scan_result: ScanResult = result.scan_result  # type: ignore[attr-defined]
    assert scan_result.any_succeeded
    assert not scan_result.all_failed
    assert all(r.succeeded for r in scan_result.source_results)


# ---------------------------------------------------------------------------
# UnifiedDiscoveryBackend — partial failures
# ---------------------------------------------------------------------------

def test_unified_ble_fails_classic_succeeds_returns_classic_devices():
    """BLE failure must not suppress Classic results."""
    classic = _classic_device()
    result = asyncio.run(
        UnifiedDiscoveryBackend(
            FakeBackend(DiscoveryError("BLE adapter off")),
            FakeBackend([classic]),
        ).scan(1)
    )
    assert len(result) == 1
    assert result[0].source is DiscoverySource.WINDOWS_PAIRED_CLASSIC


def test_unified_ble_fails_scan_result_records_ble_failure():
    classic = _classic_device()
    result = asyncio.run(
        UnifiedDiscoveryBackend(
            FakeBackend(DiscoveryError("BLE adapter off")),
            FakeBackend([classic]),
        ).scan(1)
    )
    sr: ScanResult = result.scan_result  # type: ignore[attr-defined]
    ble_result = next(r for r in sr.source_results if "BLE" in r.source_name)
    assert not ble_result.succeeded
    assert "BLE adapter off" in (ble_result.error or "")


def test_unified_classic_fails_ble_succeeds_returns_ble_devices(device: DeviceObservation):
    """Classic failure must not suppress BLE results."""
    result = asyncio.run(
        UnifiedDiscoveryBackend(
            FakeBackend([device]),
            FakeBackend(DiscoveryError("access denied")),
        ).scan(1)
    )
    assert len(result) == 1
    assert result[0].source is DiscoverySource.BLE_ADVERTISEMENT


def test_unified_classic_fails_scan_result_records_classic_failure(device: DeviceObservation):
    result = asyncio.run(
        UnifiedDiscoveryBackend(
            FakeBackend([device]),
            FakeBackend(DiscoveryError("access denied")),
        ).scan(1)
    )
    sr: ScanResult = result.scan_result  # type: ignore[attr-defined]
    classic_result = next(r for r in sr.source_results if "Classic" in r.source_name)
    assert not classic_result.succeeded
    assert "access denied" in (classic_result.error or "")


def test_unified_partial_failure_status_summary_names_both_sources(device: DeviceObservation):
    result = asyncio.run(
        UnifiedDiscoveryBackend(
            FakeBackend([device]),
            FakeBackend(DiscoveryError("0x80070005 access denied")),
        ).scan(1)
    )
    sr: ScanResult = result.scan_result  # type: ignore[attr-defined]
    summary = sr.status_summary()
    assert "BLE" in summary
    assert "Classic" in summary
    assert "failed" in summary.lower()


# ---------------------------------------------------------------------------
# UnifiedDiscoveryBackend — all sources fail
# ---------------------------------------------------------------------------

def test_unified_raises_when_every_source_is_unavailable():
    backend = UnifiedDiscoveryBackend(
        FakeBackend(DiscoveryError("BLE unavailable")),
        FakeBackend(DiscoveryError("Classic unavailable")),
    )
    with pytest.raises(DiscoveryError, match="BLE unavailable.*Classic unavailable"):
        asyncio.run(backend.scan(1))


def test_unified_all_fail_error_message_contains_both_source_errors():
    backend = UnifiedDiscoveryBackend(
        FakeBackend(DiscoveryError("adapter off")),
        FakeBackend(DiscoveryError("access denied")),
    )
    with pytest.raises(DiscoveryError) as exc_info:
        asyncio.run(backend.scan(1))
    message = str(exc_info.value)
    assert "adapter off" in message
    assert "access denied" in message


# ---------------------------------------------------------------------------
# SourceResult and ScanResult helpers
# ---------------------------------------------------------------------------

def test_source_result_succeeded_when_no_error():
    sr = SourceResult("BLE", observations=[])
    assert sr.succeeded


def test_source_result_failed_when_error_is_set():
    sr = SourceResult("BLE", error="adapter off")
    assert not sr.succeeded


def test_scan_result_all_failed():
    sr = ScanResult(
        devices=[],
        source_results=[
            SourceResult("BLE", error="err1"),
            SourceResult("Classic", error="err2"),
        ],
    )
    assert sr.all_failed
    assert not sr.any_succeeded


def test_scan_result_any_succeeded():
    sr = ScanResult(
        devices=[],
        source_results=[
            SourceResult("BLE", observations=[]),
            SourceResult("Classic", error="err"),
        ],
    )
    assert sr.any_succeeded
    assert not sr.all_failed


def test_scan_result_status_summary_includes_counts_and_errors():
    from datetime import datetime, timezone
    d = DeviceObservation("ble:x", "X", "x", Transport.BLE, None, datetime.now(timezone.utc))
    sr = ScanResult(
        devices=[d],
        source_results=[
            SourceResult("BLE", observations=[d]),
            SourceResult("Classic", error="access denied"),
        ],
    )
    summary = sr.status_summary()
    assert "1 device(s)" in summary
    assert "access denied" in summary
