"""Stable types shared by Bluetooth discovery and rename providers."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol


class Transport(str, Enum):
    BLE = "BLE"
    CLASSIC = "Classic Bluetooth"
    PAIRED = "Paired record"


class DiscoverySource(str, Enum):
    BLE_ADVERTISEMENT = "BLE advertisement"
    WINDOWS_PAIRED_CLASSIC = "Windows paired Bluetooth"


class RenameStatus(str, Enum):
    NOT_SUPPORTED = "not_supported"
    INVALID_NAME = "invalid_name"
    ACKNOWLEDGED_UNVERIFIED = "acknowledged_unverified"
    TRANSPORT_ERROR = "transport_error"


@dataclass(frozen=True)
class DeviceObservation:
    """Data observed from Windows/BLE, not a guarantee of persistent device state."""

    key: str
    name: str | None
    address: str | None
    transport: Transport
    rssi_dbm: int | None
    seen_at: datetime
    source: DiscoverySource = DiscoverySource.BLE_ADVERTISEMENT
    service_uuids: tuple[str, ...] = ()
    manufacturer_ids: tuple[int, ...] = ()
    paired: bool | None = None


@dataclass(frozen=True)
class RenameRequest:
    device: DeviceObservation
    name: str


@dataclass(frozen=True)
class RenameResult:
    status: RenameStatus
    message: str
    provider_id: str | None = None


class RenameProvider(Protocol):
    """A provider is allowed only for a verified device-specific protocol."""

    provider_id: str

    def supports(self, device: DeviceObservation) -> bool: ...

    async def rename(self, request: RenameRequest) -> RenameResult: ...

