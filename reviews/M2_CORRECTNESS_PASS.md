# M2 Correctness Pass — Antigravity Audit Report

**Date:** 2026-10-18  
**Author:** Antigravity (primary developer, post-handoff)  
**Evidence:** `pytest -v`: **45 passed** (was 16); offscreen GUI smoke test: **4/4 passed**; `compileall`: **clean**.

---

## Changes made

### `src/tws_name_changer/bluetooth/discovery.py`

| Change | Rationale |
|---|---|
| Added `SourceResult` dataclass | Carries per-source name, observation list, and error string. |
| Added `ScanResult` dataclass | Groups all devices with the list of `SourceResult` objects and provides `any_succeeded`, `all_failed`, and `status_summary()`. |
| Added `_AnnotatedList` | A `list` subclass that attaches `scan_result` so the UI can retrieve rich partial-failure info from the plain return value without changing the `DiscoveryBackend` Protocol signature. |
| `UnifiedDiscoveryBackend.scan` rewritten | Uses `_to_source_result()` helpers to build `SourceResult` per source; wraps merged device list in `_AnnotatedList`; raises `DiscoveryError` only when **all** sources fail. |
| `WindowsPairedClassicBackend.scan` — combined `except` clause | WinRT raises `OSError` (winerror `-2147024891`) in practice, not `PermissionError`. Both are now caught together and routed to `_classic_adapter_message`. |
| `_ble_adapter_message` improved | Expanded to three concrete numbered steps: turn on Bluetooth, check Device Manager driver, ensure Bluetooth Support Service is running. |
| `_classic_adapter_message` added | New helper for the access-denied case (0x80070005 / E_ACCESSDENIED): explains the Windows 11 Privacy & Security > Bluetooth setting; explicitly states administrator privileges are not required. |

### `src/tws_name_changer/ui/main_window.py`

| Change | Rationale |
|---|---|
| `_show_devices` inspects `_AnnotatedList` | Shows per-source success/failure breakdown in the status label. Partial-failure is labelled clearly. |
| `_show_scan_error` handler extracted | Separates scan-wide failures from device-list update. |

### `tests/test_discovery.py`

Rewritten from 9 discovery tests → **39 discovery tests** covering:

- `_clean_name` edge cases (empty string → None, truncation to 248 chars)
- BLE error messages (0x800710DF specific text, generic fallback)
- Classic error messages (0x80070005 via `OSError` and via `PermissionError`, generic fallback)
- `BleakDiscoveryBackend` negative timeout, mocked `OSError`
- `WindowsPairedClassicBackend`: mocked success, `OSError` winerror -2147024891, `PermissionError`, `ImportError`, negative timeout
- `merge_observations`: different addresses, same key deduplication (newer wins), empty list, single device
- `UnifiedDiscoveryBackend`: both succeed, `_AnnotatedList` attached, `ScanResult.source_results` all-succeed; BLE-fails/Classic-succeeds; Classic-fails/BLE-succeeds; failure recorded in `scan_result`; partial summary names both sources; all-fail raises combined error
- `SourceResult` / `ScanResult` helpers: `succeeded`, `all_failed`, `any_succeeded`, `status_summary`

---

## Windows hardware findings (unchanged from prior audit)

| Error code | Condition | Diagnosis |
|---|---|---|
| `0x800710DF` / `ERROR_DEVICE_NOT_AVAILABLE` | BLE watcher — Bleak/WinRT | Bluetooth turned off or adapter driver error. Not a code bug. |
| `0x80070005` / `E_ACCESSDENIED` | WinRT DeviceInformation paired enumeration | Windows Privacy & Security > Bluetooth > "Let apps access Bluetooth" is off, or the Bluetooth Support Service is not running. Does **not** require administrator rights. |

No live hardware scan was performed; adapter was not ready at the time of testing. Results above are from prior sessions.

---

## Outstanding findings (carried forward)

| ID | Severity | Finding | Status |
|---|---|---|---|
| M2-001 | High | Live BR/EDR Classic inquiry not implemented; Windows backend enumerates cached paired records only. Source labels are prominent. | Unchanged — no evidence for safe live Classic inquiry. |
| M2-002 | Medium | `asyncio.run()` on the GUI thread for rename is acceptable while rename is a no-op; must be moved to a worker before real device I/O is added. | Unchanged — blocked on M3. |
| M2-003 | Low | Live BLE scan not verified on hardware (adapter not ready). | Unchanged — hardware access required. |
| M2-004 | High | No firmware provider. Correct by design. | Unchanged. |

---

## Definition of done — M2 correctness pass

- [x] BLE and Classic sources fail independently without erasing the other's results.
- [x] Partial success is displayed accurately (per-source status in UI).
- [x] `0x800710DF` error message lists concrete steps (Bluetooth on, Device Manager, service).
- [x] `0x80070005` error message explains Privacy settings, explicitly states admin not required.
- [x] `WindowsPairedClassicBackend` catches `OSError` with winerror `-2147024891`, not only `PermissionError`.
- [x] 45 automated tests pass; 0 regressions.
- [x] Offscreen GUI smoke test passes (4 sub-tests).
- [x] Python compilation clean across all source and test files.
- [x] Documentation updated (`TASKS.md`, `PLAN.md`, this report).
