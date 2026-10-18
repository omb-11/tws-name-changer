# Plan

## Ownership and shared-workspace protocol

The workspace contained no Antigravity production files and no Git repository when this plan was updated. Codex created the initial safe foundation at the user's request. Once Antigravity supplies a worktree, it owns production changes. To avoid overwrites: work on separate Git branches/worktrees, claim files in `TASKS.md`, commit focused changes, and exchange review findings only via `reviews/`. Never overwrite a modified file without inspecting its Git diff and coordinating its owner.

## Milestones

| Milestone | Status | Acceptance criterion |
|---|---|---|
| M0 feasibility and plan | Complete | Evidence and limitations documented. |
| M1 GUI and mocked workflow | Complete | GUI launches and reports simulated/unsupported states honestly. |
| M2 Bluetooth discovery | Complete | BLE and Windows paired-Classic sources fail independently; partial failures shown in UI with per-source detail; 45 tests pass; actionable error messages for `0x800710DF` and `0x80070005`. Hardware scan blocked by adapter readiness / privacy settings. |
| M3 firmware provider | Blocked | Exact model/firmware and a verified safe method exist. |
| M4 integration/tests | In progress | 45 automated tests cover all mocked paths; hardware paths pending. |
| M5 packaging | Planned | Reproducible PyInstaller build tested on Windows 11. |
| M6 final audit | Planned | Every file and acceptance criterion independently reviewed. |

## Decisions

- `bleak` is used for cross-platform Python BLE discovery; discovery is behind `DiscoveryBackend` for tests and future native-WinRT enhancement.
- The default provider registry is empty. A `UnsupportedProvider` returns `NOT_SUPPORTED`; it never writes to a device.
- A local post-scan is not independent verification. Only a separately rescanned phone/laptop after a power cycle can substantiate an advertised-name claim.
- `ScanResult` and `SourceResult` carry per-source success/failure without changing the `DiscoveryBackend` Protocol; `_AnnotatedList` attaches `scan_result` to the returned list for the UI to inspect.
- `WindowsPairedClassicBackend` catches both `OSError` (winerror `-2147024891`) and `PermissionError` for the Windows access-denied condition; both route to `_classic_adapter_message`.
- Administrator privileges are not required for paired-device enumeration under normal Windows 11 conditions.
