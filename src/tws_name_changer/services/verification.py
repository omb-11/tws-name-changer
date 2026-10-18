"""Local observation only; independent verification is always manual."""
from __future__ import annotations

from dataclasses import dataclass
from ..bluetooth.base import DeviceObservation


@dataclass(frozen=True)
class VerificationResult:
    locally_observed: bool
    message: str


def compare_local_observation(device: DeviceObservation, expected_name: str) -> VerificationResult:
    if device.name == expected_name:
        return VerificationResult(True, "Name observed locally. Verify independently after a power cycle.")
    return VerificationResult(False, "Expected name was not observed locally.")

