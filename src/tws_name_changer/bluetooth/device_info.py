"""Helpers that make observations safe to render in a UI."""
from .base import DeviceObservation


def display_name(device: DeviceObservation) -> str:
    return device.name.strip() if device.name and device.name.strip() else "Unnamed Bluetooth device"


def capability_summary(device: DeviceObservation) -> str:
    parts = [device.transport.value]
    if device.service_uuids:
        parts.append(f"{len(device.service_uuids)} advertised service(s)")
    if device.rssi_dbm is not None:
        parts.append(f"RSSI {device.rssi_dbm} dBm")
    return " · ".join(parts)

