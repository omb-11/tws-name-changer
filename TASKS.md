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
| T9 | Antigravity | Complete | GitHub CLI & User Authorization | Created public GitHub repository `omb-11/tws-name-changer` and published release `v1.0.0` with assets and SHA-256 |
| T10 | Antigravity | Complete | Vite + React + TypeScript | Created modern download landing website in `website/`, tested production build, and added automated tests |
| T11 | OpenCode | Complete | Independent Review | Full independent release review documented in `reviews/OPENCODE_RELEASE_REVIEW.md` |
