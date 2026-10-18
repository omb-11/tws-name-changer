"""BLE discovery behind a small asynchronous interface."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol

from .base import DeviceObservation, DiscoverySource, Transport

logger = logging.getLogger(__name__)


class DiscoveryBackend(Protocol):
    async def scan(self, timeout_seconds: float) -> list[DeviceObservation]: ...


class DiscoveryError(RuntimeError):
    """A source-specific discovery failure suitable for display to the user."""


@dataclass(frozen=True)
class SourceResult:
    """Outcome of scanning a single source, carrying both observations and any error."""
    source_name: str
    observations: list[DeviceObservation] = field(default_factory=list)
    error: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.error is None


@dataclass(frozen=True)
class ScanResult:
    """Combined result of all discovery sources, including partial-failure details."""
    devices: list[DeviceObservation]
    source_results: list[SourceResult]

    @property
    def any_succeeded(self) -> bool:
        return any(r.succeeded for r in self.source_results)

    @property
    def all_failed(self) -> bool:
        return all(not r.succeeded for r in self.source_results)

    def status_summary(self) -> str:
        """Human-readable summary of which sources succeeded or failed."""
        parts: list[str] = []
        for r in self.source_results:
            if r.succeeded:
                parts.append(f"{r.source_name}: {len(r.observations)} device(s) found")
            else:
                parts.append(f"{r.source_name}: failed — {r.error}")
        return "\n".join(parts)


class BleakDiscoveryBackend:
    """Real BLE discovery. Importing the package does not require an adapter."""

    async def scan(self, timeout_seconds: float = 8.0) -> list[DeviceObservation]:
        if timeout_seconds <= 0:
            raise ValueError("Scan timeout must be positive")
        try:
            from bleak import BleakScanner
        except ImportError as error:  # pragma: no cover - packaging failure
            raise DiscoveryError("BLE discovery dependency is not installed") from error

        logger.debug("BLE scan starting (timeout=%.1fs)", timeout_seconds)
        try:
            discovered = await asyncio.wait_for(
                BleakScanner.discover(timeout=timeout_seconds, return_adv=True), timeout_seconds + 2
            )
        except OSError as error:
            winerr = getattr(error, "winerror", None)
            hex_err = f"0x{winerr & 0xFFFFFFFF:08X}" if winerr else "N/A"
            logger.warning("BLE scan failed: %s (winerror=%s)", error, hex_err)
            raise DiscoveryError(_ble_adapter_message(error)) from error
        logger.debug("BLE scan completed: %d device(s) found", len(discovered))
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
    """Enumerate Windows paired Bluetooth records via WinRT, not live BR/EDR inquiry.

    This backend enumerates **paired/cached** Bluetooth Classic (BR/EDR) device
    records stored by Windows. It does NOT perform a live BR/EDR inquiry — it
    only reads the Windows device registry. Devices are returned whether they are
    currently in range or not. ``is_paired`` reflects the cached pairing state;
    it may show False for known devices that have been removed from the pairing
    table but remain in the AEP cache.

    Implementation note: WinRT returns a ``DeviceInformationCollection`` that does
    not support Python ``for``-loop iteration (requires the uninstalled
    ``winrt.windows.foundation.collections`` package). This backend uses
    ``range(len(records))`` + index access, which works correctly.
    """

    def __init__(self, api_loader: object | None = None) -> None:
        self._api_loader = api_loader

    async def scan(self, timeout_seconds: float = 8.0) -> list[DeviceObservation]:
        if timeout_seconds <= 0:
            raise ValueError("Scan timeout must be positive")
        try:
            BluetoothDevice, DeviceInformation = self._load_api()
        except ImportError as error:
            raise DiscoveryError("Windows paired-device discovery components are not installed") from error
        logger.debug("Windows paired-Classic scan starting")
        try:
            selector = BluetoothDevice.get_device_selector()
            records = await asyncio.wait_for(DeviceInformation.find_all_async_aqs_filter(selector), timeout_seconds)
        except (PermissionError, OSError) as error:
            winerr = getattr(error, "winerror", None)
            hex_err = f"0x{winerr & 0xFFFFFFFF:08X}" if winerr else "N/A"
            logger.warning("Windows paired-Classic scan failed: %s (winerror=%s)", error, hex_err)
            raise DiscoveryError(_classic_adapter_message(error)) from error

        # IMPORTANT: Do NOT use `for record in records` — iterating a
        # DeviceInformationCollection with Python's for-loop imports
        # winrt.windows.foundation.collections, which is not installed.
        # Use range(len(records)) + index access instead.
        count = len(records)
        logger.debug("Windows paired-Classic scan: %d record(s) from cache", count)
        now = datetime.now(timezone.utc)
        observations: list[DeviceObservation] = []
        for i in range(count):
            record = records[i]
            address = _extract_address_from_id(record.id)
            if address is None:
                # Best-effort async lookup for non-standard IDs; skip silently if unavailable.
                address = await _classic_address(BluetoothDevice, record.id)
            key = f"classic:{address}" if address else f"paired:{record.id}"
            is_paired: bool | None = None
            try:
                is_paired = record.pairing.is_paired
            except Exception:
                pass
            observations.append(DeviceObservation(
                key=key, name=_clean_name(record.name), address=address,
                transport=Transport.CLASSIC, rssi_dbm=None, seen_at=now,
                source=DiscoverySource.WINDOWS_PAIRED_CLASSIC, paired=is_paired,
            ))
            logger.debug(
                "Classic record: id=%r name=%r address=%s paired=%s",
                record.id, record.name, address, is_paired,
            )
        return sorted(observations, key=lambda item: (item.name or "", item.key))

    def _load_api(self) -> tuple[object, object]:
        if self._api_loader is not None:
            return self._api_loader()  # type: ignore[operator]
        from winrt.windows.devices.bluetooth import BluetoothDevice
        from winrt.windows.devices.enumeration import DeviceInformation
        return BluetoothDevice, DeviceInformation


def _extract_address_from_id(device_id: str) -> str | None:
    """Parse a Bluetooth address from a WinRT device ID without an async round-trip.

    WinRT device IDs for Bluetooth follow the pattern:
    ``Bluetooth#Bluetooth<adapter_addr>-<device_addr>``
    where addresses use colon-separated hex bytes. Returns the device address
    as a 12-digit uppercase hex string, or None if the ID is not in that form.
    """
    # Expected form: "Bluetooth#Bluetooth64:49:7d:53:50:15-41:42:ff:85:aa:71"
    try:
        dash_idx = device_id.index("-")
        raw = device_id[dash_idx + 1:]
        # Validate: 17 chars, 5 colons, all hex
        if len(raw) == 17 and raw.count(":") == 5:
            return raw.replace(":", "").upper()
    except (ValueError, AttributeError):
        pass
    return None


async def _classic_address(bluetooth_device: object, device_id: str) -> str | None:
    """Best effort only: paired records still work if an address lookup fails.

    Note: This call requires the earbuds to be in range and the adapter active.
    It will fail with 0x800710DF when the adapter is off; that is non-fatal.
    """
    try:
        device = await bluetooth_device.from_id_async(device_id)  # type: ignore[attr-defined]
        return None if device is None else f"{int(device.bluetooth_address):012X}"
    except (OSError, PermissionError) as e:
        winerr = getattr(e, "winerror", None)
        logger.debug("_classic_address lookup failed for %r: winerror=0x%08X", device_id,
                     (winerr & 0xFFFFFFFF) if winerr else 0)
        return None


class UnifiedDiscoveryBackend:
    """Collect independent BLE and paired-Classic sources without hiding failures.

    Both sources are always attempted concurrently. A failure in one source does
    not suppress results from the other. When all sources fail, a ``DiscoveryError``
    is raised. When at least one source yields results, a ``ScanResult`` is returned
    that contains the devices *and* a ``SourceResult`` per backend so callers can
    surface partial-failure details to the user.
    """

    def __init__(self, ble: DiscoveryBackend, classic: DiscoveryBackend) -> None:
        self._ble, self._classic = ble, classic

    async def scan(self, timeout_seconds: float) -> list[DeviceObservation]:
        """Run both sources and return merged observations.

        Raises ``DiscoveryError`` only when *every* source fails so that any
        successfully discovered device is always visible. Partial failures are
        embedded in the returned ``ScanResult`` for the caller to display.
        """
        raw = await asyncio.gather(
            self._ble.scan(timeout_seconds),
            self._classic.scan(timeout_seconds),
            return_exceptions=True,
        )
        source_results = [
            _to_source_result("BLE", raw[0]),
            _to_source_result("Windows paired Classic", raw[1]),
        ]
        observations = [item for r in source_results for item in r.observations]
        failures = [r for r in source_results if not r.succeeded]

        logger.info(
            "Unified scan complete: %d device(s); %d source(s) succeeded, %d failed",
            len(observations),
            len(source_results) - len(failures),
            len(failures),
        )
        for r in source_results:
            if r.succeeded:
                logger.info("  %s: %d device(s)", r.source_name, len(r.observations))
            else:
                logger.warning("  %s: FAILED — %s", r.source_name, r.error)

        if not observations and failures:
            combined = "; ".join(r.error for r in failures if r.error)  # type: ignore[misc]
            raise DiscoveryError(combined)

        scan_result = ScanResult(devices=merge_observations(observations), source_results=source_results)
        device_list = _AnnotatedList(scan_result.devices, scan_result)
        return device_list  # type: ignore[return-value]


class _AnnotatedList(list):  # type: ignore[type-arg]
    """A plain list that also carries a ``scan_result`` attribute for the UI."""

    def __init__(self, items: list[DeviceObservation], scan_result: ScanResult) -> None:
        super().__init__(items)
        self.scan_result: ScanResult = scan_result


def _to_source_result(name: str, raw: object) -> SourceResult:
    if isinstance(raw, list):
        return SourceResult(source_name=name, observations=raw)
    error_msg = str(raw) if raw else "Unknown error"
    return SourceResult(source_name=name, error=error_msg)


def merge_observations(observations: list[DeviceObservation]) -> list[DeviceObservation]:
    """Deduplicate only exact source keys or exact non-empty addresses, never names."""
    merged: dict[str, DeviceObservation] = {}
    for device in observations:
        identity = f"address:{device.address.upper()}" if device.address else f"key:{device.key}"
        previous = merged.get(identity)
        if previous is None or device.seen_at > previous.seen_at:
            merged[identity] = device
    return sorted(merged.values(), key=lambda item: (item.name or "", item.key))


def _ble_adapter_message(error: OSError) -> str:
    winerror = getattr(error, "winerror", None)
    if winerror == -2147020577:
        return (
            "BLE scan failed — Windows reports ERROR_DEVICE_NOT_AVAILABLE (0x800710DF). "
            "Possible causes and fixes:\n"
            "  1. Bluetooth is turned off — open Windows Settings > Bluetooth & devices and turn it on.\n"
            "  2. The BluetoothUserService is stopped — toggle Bluetooth off then on in Settings "
            "to restart it, or open Services and start 'BluetoothUserService_*' manually.\n"
            "  3. The Bluetooth adapter driver has an error — open Device Manager, find the Bluetooth "
            "adapter, and reinstall or update its driver.\n"
            "After making changes, scan again."
        )
    return (
        "BLE scan failed — the Windows Bluetooth adapter is unavailable or not ready. "
        "Turn Bluetooth on, check the adapter in Device Manager, then scan again."
    )


def _classic_adapter_message(error: OSError | PermissionError) -> str:
    winerror = getattr(error, "winerror", None)
    # 0x80070005 == -2147024891 == E_ACCESSDENIED; may surface as OSError or PermissionError.
    if winerror == -2147024891 or isinstance(error, PermissionError):
        return (
            "Windows paired-device scan failed — access denied (0x80070005). "
            "Possible causes and fixes:\n"
            "  1. Bluetooth app privacy is off — open Windows Settings > Privacy & security > "
            "Bluetooth, and enable 'Let apps access Bluetooth'.\n"
            "  2. Bluetooth is turned off or the adapter is not ready — open Settings > "
            "Bluetooth & devices and check the adapter.\n"
            "  3. The Windows Bluetooth service is stopped — open Services and ensure "
            "'Bluetooth Support Service' is running.\n"
            "After making changes, scan again. Administrator privileges are not required for "
            "normal paired-device enumeration."
        )
    return (
        "Windows paired-device scan failed — the Bluetooth adapter is unavailable. "
        "Turn Bluetooth on, check the adapter in Device Manager, then scan again."
    )


def _clean_name(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = "".join(char for char in value if char.isprintable()).strip()
    return cleaned[:248] or None
