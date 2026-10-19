# Tasks

| ID | Owner | Status | Dependency | Review |
|---|---|---|---|---|
| T1 | Codex bootstrap (user-authorised) | Complete | Empty workspace | Initial project structure and protocols |
| T2 | Antigravity | Complete | T1 | Discovery and GUI implementation |
| T3 | Codex | Complete | M0 | Feasibility and architecture reports in `reviews/` |
| T4 | Antigravity | Blocked | Exact earbuds model, firmware, documented rename method | Firmware renaming honestly reported as unsupported |
| T5 | Antigravity | Complete | Intel Bluetooth adapter | Real hardware discovery validated: BLE (live nearby devices) and Windows Classic (2 cached pTron TWS records) |
| T6 | Antigravity | Complete | T2/T5 | Full final QA audit in `reviews/FINAL_QA_AUDIT.md` |
| T7 | Antigravity | Complete | Windows permissions & WinRT | Fixed WinRT collection index access, synchronous address parsing, partial failure reporting |
| T8 | Antigravity | Complete | PyInstaller packaging | Fixed PySide6 packaging defect; built and verified standalone `dist/TWSNameChanger.exe` and `build.ps1` |
