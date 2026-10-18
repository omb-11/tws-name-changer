# M0 architecture and test-strategy review

**Reviewer:** OpenAI Codex  
**Date:** 2026-10-18  
**Status:** Recommendations for the production owner; no production files changed.

## Recommended M1/M2 boundary

Build the application as an **evidence-led diagnostic application first**. A provider registry should be empty by default. The user can scan, inspect observations, and receive `Unsupported: no verified provider for this model/firmware`; no UI action may alter a Windows alias or imply a remote rename.

Use Windows WinRT APIs as the discovery authority on Windows, exposed through a narrow adapter. `BluetoothLEAdvertisementWatcher` receives current LE advertisements, and its received-event arguments expose the address/address type, RSSI, timestamp, connectability, scan-response state, and payload. [`BluetoothLEAdvertisementWatcher`](https://learn.microsoft.com/en-us/uwp/api/windows.devices.bluetooth.advertisement.bluetoothleadvertisementwatcher) and [`BluetoothLEAdvertisementReceivedEventArgs`](https://learn.microsoft.com/en-us/uwp/api/windows.devices.bluetooth.advertisement.bluetoothleadvertisementreceivedeventargs?view=winrt-28000) document that surface. Use `Windows.Devices.Enumeration` separately for paired/cached device records; Microsoft notes snapshot enumeration can take up to 30 seconds, so it must never run on the GUI thread. [Microsoft enumeration guidance](https://learn.microsoft.com/en-us/windows/apps/develop/devices-sensors/enumerate-devices)

## Proposed interfaces

```python
@dataclass(frozen=True)
class DeviceObservation:
    stable_key: str                 # internal, never assume universal identity
    transport: Literal["ble", "classic", "paired"]
    observed_name: str | None       # what Windows observed, not a claimed firmware name
    address: str | None             # redact in normal logs/UI export
    address_type: str | None
    rssi_dbm: int | None
    seen_at: datetime
    paired: bool | None
    connectable: bool | None
    service_uuids: tuple[str, ...]
    manufacturer_ids: tuple[int, ...]

class DiscoveryBackend(Protocol):
    async def scan(self, timeout_s: float) -> list[DeviceObservation]: ...

class RenameProvider(Protocol):
    id: str
    def supports(self, device: DeviceObservation) -> SupportAssessment: ...
    async def rename(self, request: RenameRequest) -> RenameAttempt: ...

class VerificationBackend(Protocol):
    async def observe_after_reconnect(
        self, target: TargetFingerprint, expected_name: str, timeout_s: float
    ) -> VerificationResult: ...
```

Constraints:

- `stable_key` must make transport and address type explicit. Do not treat a random/private LE address as a durable identity.
- Model/firmware identification is required for `RenameProvider.supports`; a name match, OUI, or service UUID alone is insufficient.
- `RenameAttempt` needs distinct statuses: `NOT_SUPPORTED`, `USER_CANCELLED`, `TRANSPORT_ERROR`, `DEVICE_REJECTED`, `ACKNOWLEDGED_UNVERIFIED`, and `INDEPENDENTLY_VERIFIED`.
- `VerificationBackend` can establish only *local* post-reconnect observation. A second-device check must remain a manual, explicitly recorded acceptance gate.

## Threading and UI

- Keep all WinRT/Bluetooth callbacks and discovery work outside the Qt GUI thread; marshal immutable results back with Qt signals.
- Disable only the action in flight, preserve scan cancellation, and bound every await with a timeout.
- Surface watcher `Stopped`/`Aborted` conditions; `Start()` can immediately enter `Aborted` on failure. [Microsoft API reference](https://learn.microsoft.com/en-us/uwp/api/windows.devices.bluetooth.advertisement.bluetoothleadvertisementwatcher.start?view=winrt-26100)
- Scan records should age out visually; an LE out-of-range event may have RSSI `-127`, per [Microsoft's event-args documentation](https://learn.microsoft.com/en-us/uwp/api/windows.devices.bluetooth.advertisement.bluetoothleadvertisementreceivedeventargs?view=winrt-28000).

## Dependency and packaging review criteria

1. Pin Python dependencies in `requirements.txt` and mirror compatible bounds in `pyproject.toml`; avoid duplicate, diverging dependency declarations.
2. Pick one Windows BLE access path and wrap it. If using Bleak for a verified provider, it offers GATT writes but does not create entitlement to write a characteristic or prove persistence. [Bleak API documentation](https://bleak.readthedocs.io/_/downloads/en/stable/pdf/)
3. Do not require elevated privileges by default. Never package secrets, device addresses, pairing material, or captured advertisement payloads as support data.
4. Establish a clean virtual environment and lock/record exact build versions before adding PyInstaller. A one-file executable should be tested on a Windows 11 machine without the development environment.

## Test matrix required before release

| Test area | Minimum evidence |
|---|---|
| Data mapping | Unit tests mapping WinRT callback values into `DeviceObservation`, including absent name/address, scan response, RSSI `-127`, random address type, and malformed UTF-8/name handling. |
| Discovery service | Fake backend tests for timeout, cancellation, adapter unavailable, watcher abort, paired-only records, deduplication without conflating TWS components, and no GUI blocking. |
| Rename service | Empty registry / unsupported device, invalid name, user cancellation, provider preflight rejection, provider timeout, acknowledged-but-unverified, and provider result propagation. |
| Verification | Expected and mismatched name, device absent, ambiguous matching observations, reconnect timeout, and manual independent-scanner checklist. |
| UI | Automated Qt tests for disabled controls during operations, cancel/retry, visible transport/status distinction, and no success wording for any status below `INDEPENDENTLY_VERIFIED`. |
| Hardware | Windows 11 adapter missing/off/on; one BLE peripheral; paired Classic headset; earbuds with case open/closed; sleep/resume; disconnect/power cycle; a separately scanned phone/laptop. |
| Packaging | Fresh Windows user profile or VM: launch, adapter error, scan, logs, and no local credentials/keys written. |

## Findings for production planning

| ID | Severity | Planned area | Evidence | Suggested fix |
|---|---|---|---|---|
| M0-002 | High | Discovery | Paired enumeration and BLE advertising are different data sources and can be delayed/cached. | Model them as separate observations and annotate source/time. |
| M0-003 | High | Provider registry | No device model or firmware evidence exists in the workspace. | Ship no rename provider until a specific supported device is documented and testable. |
| M0-004 | Medium | Verification | Same display name/address is not a robust TWS identity, especially with LE privacy. | Require a target-fingerprint policy and report ambiguous verification rather than picking a candidate. |
| M0-005 | Medium | GUI | Bluetooth operations can be delayed or aborted. | Async worker boundary, cancellation, timeout, and plain-language recovery instructions. |

