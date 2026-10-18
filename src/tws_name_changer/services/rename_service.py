"""Provider selection and conservative user-name validation."""
from __future__ import annotations

from ..bluetooth.base import DeviceObservation, RenameProvider, RenameRequest, RenameResult, RenameStatus
from ..bluetooth.providers.unsupported import UnsupportedProvider


class RenameService:
    def __init__(self, providers: list[RenameProvider] | None = None) -> None:
        self._providers = providers or [UnsupportedProvider()]

    async def request_rename(self, device: DeviceObservation, new_name: str) -> RenameResult:
        issue = validate_name(new_name)
        if issue:
            return RenameResult(RenameStatus.INVALID_NAME, issue)
        provider = next((item for item in self._providers if item.supports(device)), UnsupportedProvider())
        return await provider.rename(RenameRequest(device, new_name.strip()))


def validate_name(name: str) -> str | None:
    if not name or not name.strip():
        return "Enter a non-empty name."
    if any(not char.isprintable() for char in name):
        return "Names cannot contain control characters."
    if len(name.strip().encode("utf-8")) > 248:
        return "Name exceeds the Bluetooth GAP maximum of 248 UTF-8 bytes."
    return None

