"""BLE discovery behind a small asynchronous interface."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Protocol

from .base import DeviceObservation, Transport


class DiscoveryBackend(Protocol):
    async def scan(self, timeout_seconds: float) -> list[DeviceObservation]: ...


class BleakDiscoveryBackend:
    """Real BLE discovery. Importing the package does not require an adapter."""

    async def scan(self, timeout_seconds: float = 8.0) -> list[DeviceObservation]:
        if timeout_seconds <= 0:
            raise ValueError("Scan timeout must be positive")
        try:
            from bleak import BleakScanner
        except ImportError as error:  # pragma: no cover - packaging failure
            raise RuntimeError("BLE discovery dependency is not installed") from error

        try:
            discovered = await asyncio.wait_for(
                BleakScanner.discover(timeout=timeout_seconds, return_adv=True), timeout_seconds + 2
            )
        except OSError as error:
            raise RuntimeError(
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


def _clean_name(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = "".join(char for char in value if char.isprintable()).strip()
    return cleaned[:248] or None

