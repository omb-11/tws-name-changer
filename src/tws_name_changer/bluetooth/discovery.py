"""BLE discovery behind a small asynchronous interface."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Protocol

from .base import DeviceObservation, DiscoverySource, Transport


class DiscoveryBackend(Protocol):
    async def scan(self, timeout_seconds: float) -> list[DeviceObservation]: ...


class DiscoveryError(RuntimeError):
    """A source-specific discovery failure suitable for display to the user."""


class BleakDiscoveryBackend:
    """Real BLE discovery. Importing the package does not require an adapter."""

    async def scan(self, timeout_seconds: float = 8.0) -> list[DeviceObservation]:
        if timeout_seconds <= 0:
            raise ValueError("Scan timeout must be positive")
        try:
            from bleak import BleakScanner
        except ImportError as error:  # pragma: no cover - packaging failure
            raise DiscoveryError("BLE discovery dependency is not installed") from error

        try:
            discovered = await asyncio.wait_for(
                BleakScanner.discover(timeout=timeout_seconds, return_adv=True), timeout_seconds + 2
            )
        except OSError as error:
            raise DiscoveryError(
                "Windows Bluetooth adapter is unavailable or not ready. Turn Bluetooth on, "
                "check the adapter in Device Manager, then scan again."
            ) from error
        now = datetime.now(timezone.utc)
        observations: list[DeviceObservation] = []
        for address, (device, advertisement) in discovered.items():
            local_name = advertisement.local_name or device.name
            observations.append(DeviceObservation(
                key=f"ble:{address}", name=_clean_name(local_name), address=address,
                transport=Transport.BLE, rssi_dbm=advertisement.rssi, seen_at=now,
                service_uuids=tuple(str(item) for item in advertisement.service_uuids),
                manufacturer_ids=tuple(advertisement.manufacturer_data.keys()),
            ))
        return sorted(observations, key=lambda item: (item.name or "", item.key))


class WindowsPairedClassicBackend:
    """Enumerate Windows paired Bluetooth records via WinRT, not live BR/EDR inquiry."""

    def __init__(self, api_loader: object | None = None) -> None:
        self._api_loader = api_loader

    async def scan(self, timeout_seconds: float = 8.0) -> list[DeviceObservation]:
        if timeout_seconds <= 0:
            raise ValueError("Scan timeout must be positive")
        try:
            BluetoothDevice, DeviceInformation = self._load_api()
        except ImportError as error:
            raise DiscoveryError("Windows paired-device discovery components are not installed") from error
        try:
            selector = BluetoothDevice.get_device_selector()
            records = await asyncio.wait_for(DeviceInformation.find_all_async_aqs_filter(selector), timeout_seconds)
        except PermissionError as error:
            raise DiscoveryError(
                "Windows denied paired Bluetooth-device access. Check Bluetooth and app privacy permissions, then scan again."
            ) from error
        except OSError as error:
            raise DiscoveryError("Windows paired Bluetooth enumeration is unavailable. Check the Bluetooth adapter.") from error
        now = datetime.now(timezone.utc)
        observations: list[DeviceObservation] = []
        for record in records:
            address = await _classic_address(BluetoothDevice, record.id)
            key = f"classic:{address}" if address else f"paired:{record.id}"
            observations.append(DeviceObservation(
                key=key, name=_clean_name(record.name), address=address,
                transport=Transport.CLASSIC, rssi_dbm=None, seen_at=now,
                source=DiscoverySource.WINDOWS_PAIRED_CLASSIC, paired=record.pairing.is_paired,
            ))
        return sorted(observations, key=lambda item: (item.name or "", item.key))

    def _load_api(self) -> tuple[object, object]:
        if self._api_loader is not None:
            return self._api_loader()  # type: ignore[operator]
        from winrt.windows.devices.bluetooth import BluetoothDevice
        from winrt.windows.devices.enumeration import DeviceInformation
        return BluetoothDevice, DeviceInformation


async def _classic_address(bluetooth_device: object, device_id: str) -> str | None:
    """Best effort only: paired records still work if an address lookup fails."""
    try:
        device = await bluetooth_device.from_id_async(device_id)  # type: ignore[attr-defined]
        return None if device is None else f"{int(device.bluetooth_address):012X}"
    except (OSError, PermissionError):
        return None


class UnifiedDiscoveryBackend:
    """Collect independent BLE and paired-Classic sources without hiding failures."""
    def __init__(self, ble: DiscoveryBackend, classic: DiscoveryBackend) -> None:
        self._ble, self._classic = ble, classic

    async def scan(self, timeout_seconds: float) -> list[DeviceObservation]:
        results = await asyncio.gather(self._ble.scan(timeout_seconds), self._classic.scan(timeout_seconds), return_exceptions=True)
        observations = [item for result in results if isinstance(result, list) for item in result]
        failures = [result for result in results if isinstance(result, Exception)]
        if not observations and failures:
            raise DiscoveryError("; ".join(str(error) for error in failures))
        return merge_observations(observations)


def merge_observations(observations: list[DeviceObservation]) -> list[DeviceObservation]:
    """Deduplicate only exact source keys or exact non-empty addresses, never names."""
    merged: dict[str, DeviceObservation] = {}
    for device in observations:
        identity = f"address:{device.address.upper()}" if device.address else f"key:{device.key}"
        previous = merged.get(identity)
        if previous is None or device.seen_at > previous.seen_at:
            merged[identity] = device
    return sorted(merged.values(), key=lambda item: (item.name or "", item.key))


def _clean_name(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = "".join(char for char in value if char.isprintable()).strip()
    return cleaned[:248] or None

