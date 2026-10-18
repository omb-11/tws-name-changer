# Architecture

| File/module | Purpose and public interface | Dependencies | Tests |
|---|---|---|---|
| `main.py` | Starts application via `run()` | `app` | Manual launch |
| `app.py` | Wires Qt UI and services | PySide6, UI | Manual launch |
| `ui/main_window.py` | Device list and non-blocking scan UI | PySide6, `DiscoveryService`, `RenameService` | Manual/UI follow-up |
| `bluetooth/base.py` | Immutable device/result models and provider protocol | stdlib | service tests |
| `bluetooth/discovery.py` | BLE scan backend and discovery protocol; Classic backend intentionally not implemented | bleak (optional at import) | discovery tests |
| `bluetooth/device_info.py` | Presents observed capability metadata | base | discovery tests |
| `bluetooth/providers/unsupported.py` | Honest default provider | base | rename tests |
| `services/rename_service.py` | Validates request, selects provider, never claims verification | base | rename tests |
| `services/verification.py` | Classifies local scan evidence only | base | verification tests |
| `storage/settings.py` | Minimal JSON UI preferences; no secrets | stdlib | manual follow-up |
| `utils/logging_config.py` | Privacy-conscious local logging | stdlib | manual follow-up |

Data flow: UI → `DiscoveryService` → backend → `DeviceObservation`; UI → `RenameService` → provider → `RenameResult`. Verification is distinct and cannot produce an independent-verification claim.

`BleakDiscoveryBackend` yields live BLE advertising observations only. A future Windows Classic adapter must be independently implemented and tested; do not merge paired/cached Classic records with live BLE observations.

