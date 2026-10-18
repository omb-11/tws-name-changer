# Tasks

| ID | Owner | Status | Dependency | Review |
|---|---|---|---|---|
| T1 | Codex bootstrap (user-authorised) | Complete | Empty workspace | Pending Antigravity handoff |
| T2 | Antigravity | Complete | T1 | 45 tests pass; offscreen GUI smoke pass; M2 correctness pass done — see `reviews/M2_CORRECTNESS_PASS.md`; real hardware pending |
| T3 | Codex | Complete | M0 | Reports in `reviews/` |
| T4 | Antigravity | Blocked | Exact earbuds model, firmware, documented rename method | No provider may be added without evidence |
| T5 | Antigravity | Blocked | Usable Windows Bluetooth adapter and physical device | BLE watcher failed `0x800710DF` (Bluetooth off); paired-record query failed `0x80070005` (Privacy settings). Both produce actionable messages now. |
| T7 | Antigravity | Complete | Usable Windows Bluetooth permissions and paired Classic device | `WindowsPairedClassicBackend` now catches `OSError` with winerror `-2147024891`; partial-failure surfaces in UI via `ScanResult`/`SourceResult` |
| T6 | Codex | Planned | T2/T5 | Full final audit |
