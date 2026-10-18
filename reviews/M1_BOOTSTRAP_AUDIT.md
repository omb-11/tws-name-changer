# M1 bootstrap audit

**Date:** 2026-10-18  
**Scope:** User-authorised initial foundation because the workspace had no Antigravity files or Git repository.

## Evidence checked

- `python -m compileall -q src main.py` completed successfully.
- Dependency-free smoke check constructed an observation and confirmed `RenameService` returns `NOT_SUPPORTED` with “No command was sent.”
- Full `pytest` and GUI launch are **not yet verified**: the environment initially had no `pytest`; the pinned dependency install timed out downloading `PySide6-Essentials` from PyPI. This is an environment/network limitation, not a passing result.

## Findings

| ID | Severity | File | Evidence | Resolution |
|---|---|---|---|---|
| M1-001 | Medium | `bluetooth/discovery.py` | Current backend scans BLE only. It does not enumerate paired/classic devices. | Keep the UI/documentation specific to BLE until a separately tested Windows paired/classic adapter is implemented. |
| M1-002 | Medium | `ui/main_window.py` | Rename check uses a short `asyncio.run` on the UI thread. Current provider returns immediately; future providers will perform I/O. | Before adding a real provider, move rename orchestration to a Qt worker and add cancellation/timeout tests. |
| M1-003 | High | Entire provider registry | There is no device-specific protocol evidence. | Do not add any remote-write provider without satisfying `docs/FEASIBILITY.md` admission requirements. |
| M1-004 | Medium | `tests/` | Tests exist but have not run due dependency download timeout. | Retry in a network-capable environment; record exact output before release. |

## Handoff notes

This baseline contains no Bluetooth writes. Antigravity should inspect the uncommitted foundation before taking ownership, use a Git branch/worktree once the repository is initialized, and keep all future Codex review notes in `reviews/`.

