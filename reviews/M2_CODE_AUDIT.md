# M2 code audit

**Date:** 2026-10-18  
**Evidence:** `pytest -q`: **10 passed**; offscreen PySide6 window launch: **passed**. Neither test accesses Bluetooth hardware.

| ID | Severity | File | Finding | Required follow-up |
|---|---|---|---|---|
| M2-001 | High | `bluetooth/discovery.py` | `BleakDiscoveryBackend` only receives BLE advertisements; it does not discover Classic BR/EDR TWS devices. | Keep UI/docs BLE-specific. Add a distinct Windows Classic/paired backend only after physical Windows testing. |
| M2-002 | Medium | `ui/main_window.py` | The current immediate unsupported-provider call runs on the GUI thread. | Move a real provider operation to a worker with cancellation/timeout before adding any device I/O. |
| M2-003 | Medium | `bluetooth/discovery.py` | Real adapter-off, permission, and Windows API behavior are not covered by mocks or physical test. | Execute `docs/TESTING.md` hardware checklist on Windows 11 and retain exact errors/results. |
| M2-004 | High | Provider registry | No verified provider exists, which is correct. | Preserve default `UnsupportedProvider`; do not add generic GAP writes. |

