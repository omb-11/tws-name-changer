# M2 code audit

**Date:** 2026-10-18  
**Evidence:** `pytest -q`: **10 passed**; offscreen PySide6 window launch: **passed**. Neither test accesses Bluetooth hardware.

## Windows hardware attempt

On 2026-10-18, a 5-second read-only BLE scan reached Bleak's Windows watcher but failed before receiving observations with: `OSError: [WinError -2147020577] The device is not ready for use`. A supported WinRT paired-Bluetooth enumeration then failed with: `PermissionError: [WinError -2147024891] Access is denied.` Neither result demonstrates discovery success or failure for any earbuds. The application now translates these conditions into distinct adapter-readiness and permission recovery messages.

| ID | Severity | File | Finding | Required follow-up |
|---|---|---|---|---|
| M2-001 | High | `bluetooth/discovery.py` | Live Classic BR/EDR inquiry is still not implemented; the added Windows backend enumerates paired/cached records only. | Keep source labels prominent and validate with paired Classic hardware. |
| M2-002 | Medium | `ui/main_window.py` | The current immediate unsupported-provider call runs on the GUI thread. | Move a real provider operation to a worker with cancellation/timeout before adding any device I/O. |
| M2-003 | Medium | `bluetooth/discovery.py` | Mocked adapter and merge paths are covered, but this machine's adapter readiness/permission prevents a successful live scan. | Execute `docs/TESTING.md` hardware checklist on a Windows 11 machine with Bluetooth ready and permissions granted. |
| M2-004 | High | Provider registry | No verified provider exists, which is correct. | Preserve default `UnsupportedProvider`; do not add generic GAP writes. |

