# Architecture

| File/module | Purpose and public interface | Dependencies | Tests |
|---|---|---|---|
| `main.py` | Starts application via `run()` | `app` | Manual launch |
| `app.py` | Wires Qt UI and services | PySide6, UI | Manual launch |
| `ui/main_window.py` | Device list and non-blocking scan UI | PySide6, `DiscoveryService`, `RenameService` | Manual/UI follow-up |
| `bluetooth/base.py` | Immutable device/result models and provider protocol | stdlib | service tests |
| `bluetooth/discovery.py` | Independent BLE-advertisement and Windows paired-Bluetooth backends plus safe merger | bleak, PyWinRT (optional at import) | discovery tests |
| `bluetooth/device_info.py` | Presents observed capability metadata | base | discovery tests |
| `bluetooth/providers/unsupported.py` | Honest default provider | base | rename tests |
| `services/rename_service.py` | Validates request, selects provider, never claims verification | base | rename tests |
| `services/verification.py` | Classifies local scan evidence only | base | verification tests |
| `storage/settings.py` | Minimal JSON UI preferences; no secrets | stdlib | manual follow-up |
| `utils/logging_config.py` | Privacy-conscious local logging | stdlib | manual follow-up |

Data flow: UI → `DiscoveryService` → backend → `DeviceObservation`; UI → `RenameService` → provider → `RenameResult`. Verification is distinct and cannot produce an independent-verification claim.

`BleakDiscoveryBackend` yields live BLE advertising observations only. `WindowsPairedClassicBackend` yields paired/cached Windows records, not a live Classic inquiry. `UnifiedDiscoveryBackend` merges only exact address/key identities; it never deduplicates on display name.

