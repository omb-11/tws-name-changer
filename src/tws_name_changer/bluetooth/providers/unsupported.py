"""Default provider used until a safe, verified provider is available."""
from ..base import DeviceObservation, RenameRequest, RenameResult, RenameStatus


class UnsupportedProvider:
    provider_id = "unsupported"

    def supports(self, device: DeviceObservation) -> bool:
        return True

    async def rename(self, request: RenameRequest) -> RenameResult:
        return RenameResult(
            RenameStatus.NOT_SUPPORTED,
            "Firmware-level renaming is not supported for this device. No command was sent.",
            self.provider_id,
        )

