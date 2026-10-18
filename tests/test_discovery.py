import asyncio
import sys
from datetime import timedelta
from types import SimpleNamespace
import pytest
from tws_name_changer.bluetooth.base import DiscoverySource, DeviceObservation, Transport
from tws_name_changer.bluetooth.discovery import BleakDiscoveryBackend, DiscoveryError, UnifiedDiscoveryBackend, WindowsPairedClassicBackend, _ble_adapter_message, _clean_name, merge_observations
from tws_name_changer.bluetooth.device_info import display_name

def test_clean_name_removes_control_characters():
    assert _clean_name(" Bud\x00s\n ") == "Buds"

def test_clean_name_missing_is_missing():
    assert _clean_name(None) is None

def test_display_name_for_missing_name(device):
    assert display_name(device.__class__(**{**device.__dict__, "name": None})) == "Unnamed Bluetooth device"


class FakeBackend:
    def __init__(self, result): self.result = result
    async def scan(self, timeout_seconds):
        if isinstance(self.result, Exception): raise self.result
        return self.result


def test_unified_list_keeps_ble_and_paired_classic_sources(device):
    classic = DeviceObservation("paired:one", "Example Buds", None, Transport.CLASSIC, None, device.seen_at,
                                source=DiscoverySource.WINDOWS_PAIRED_CLASSIC, paired=True)
    result = asyncio.run(UnifiedDiscoveryBackend(FakeBackend([device]), FakeBackend([classic])).scan(1))
    assert {item.source for item in result} == {DiscoverySource.BLE_ADVERTISEMENT, DiscoverySource.WINDOWS_PAIRED_CLASSIC}


def test_merge_uses_exact_address_not_name(device):
    classic = DeviceObservation("classic:AA:BB", "Different display name", "AA:BB", Transport.CLASSIC, None,
                                device.seen_at + timedelta(seconds=1), source=DiscoverySource.WINDOWS_PAIRED_CLASSIC)
    assert merge_observations([device, classic]) == [classic]


def test_unified_raises_when_every_source_is_unavailable():
    backend = UnifiedDiscoveryBackend(FakeBackend(DiscoveryError("BLE unavailable")), FakeBackend(DiscoveryError("Classic unavailable")))
    with pytest.raises(DiscoveryError, match="BLE unavailable.*Classic unavailable"):
        asyncio.run(backend.scan(1))


def test_ble_adapter_os_error_becomes_actionable(monkeypatch):
    class Scanner:
        @classmethod
        async def discover(cls, **kwargs):
            raise OSError("not ready")
    monkeypatch.setitem(sys.modules, "bleak", SimpleNamespace(BleakScanner=Scanner))
    with pytest.raises(DiscoveryError, match="adapter is unavailable or not ready"):
        asyncio.run(BleakDiscoveryBackend().scan(1))


def test_known_windows_ble_hresult_has_specific_diagnosis():
    error = OSError("device not ready")
    error.winerror = -2147020577
    assert "0x800710DF" in _ble_adapter_message(error)


def test_windows_paired_backend_labels_mocked_classic_record():
    class BluetoothDevice:
        @staticmethod
        def get_device_selector(): return "selector"
        @staticmethod
        async def from_id_async(device_id): return SimpleNamespace(bluetooth_address=0xAABBCCDDEEFF)
    class DeviceInformation:
        @staticmethod
        async def find_all_async_aqs_filter(selector):
            return [SimpleNamespace(id="device-id", name="Classic Buds", pairing=SimpleNamespace(is_paired=True))]
    backend = WindowsPairedClassicBackend(lambda: (BluetoothDevice, DeviceInformation))
    result = asyncio.run(backend.scan(1))
    assert result[0].source is DiscoverySource.WINDOWS_PAIRED_CLASSIC
    assert result[0].transport is Transport.CLASSIC
    assert result[0].address == "AABBCCDDEEFF"
