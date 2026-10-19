# Plan

## Ownership and shared-workspace protocol

The workspace uses a coordinated Git workflow. Changes are verified with automated test suites, bytecode compilation, and executable verification before committing.

## Milestones

| Milestone | Status | Acceptance criterion |
|---|---|---|
| M0 feasibility and plan | Complete | Evidence and limitations documented in `docs/FEASIBILITY.md`. |
| M1 GUI and mocked workflow | Complete | GUI launches and reports simulated/unsupported states honestly. |
| M2 Bluetooth discovery | Complete | BLE and Windows paired-Classic sources fail independently; partial failures shown in UI with per-source detail; actionable error messages for `0x800710DF` and `0x80070005`. |
| M3 firmware provider | Blocked | Exact model/firmware and verified safe method required. Kept strictly unsupported to avoid bricking hardware. |
| M4 integration/tests | Complete | 59 automated tests cover all mocked paths, GUI flows, and settings. Real Intel Bluetooth adapter verified for BLE and Classic. |
| M5 packaging | Complete | Reproducible PyInstaller build verified on Windows 11 (`dist/TWSNameChanger.exe`, `build.ps1`, `installer/setup.iss`). |
| M6 final audit | Complete | Full QA audit completed and documented in `reviews/FINAL_QA_AUDIT.md`. |

## Decisions

- `bleak` is used for cross-platform Python BLE discovery; discovery is behind `DiscoveryBackend` for tests and native-WinRT enhancement.
- The default provider registry is empty. An `UnsupportedProvider` returns `NOT_SUPPORTED`; it never writes to a device.
- A local post-scan or Windows alias change is not independent verification. Only a separately rescanned phone/laptop after a power cycle can substantiate an advertised-name claim.
- `ScanResult` and `SourceResult` carry per-source success/failure without changing the `DiscoveryBackend` Protocol; `_AnnotatedList` attaches `scan_result` to the returned list for the UI to inspect.
- `WindowsPairedClassicBackend` uses indexed collection iteration (`range(len(records))`) to avoid missing collection dependencies, and uses `_extract_address_from_id` for synchronous MAC extraction.
- Packaging runs strictly within the virtual environment (`.venv`) with complete PySide6, Bleak, and WinRT collection hooks.
