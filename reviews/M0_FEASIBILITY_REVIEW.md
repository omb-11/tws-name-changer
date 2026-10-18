# M0 independent feasibility review

**Reviewer:** OpenAI Codex  
**Date:** 2026-10-18  
**Scope:** Empty project directory; no implementation was reviewed. This report is for the production owner to incorporate into `docs/FEASIBILITY.md`, `PLAN.md`, and `TASKS.md`.

## Verdict

Do **not** promise or implement a universal firmware-name change. Windows can discover remote Bluetooth devices and can publish advertisements for the *local Windows machine*, but the inspected platform surface does not provide a generic operation that rewrites a remote earbud's advertising or Classic Bluetooth name. Firmware-level renaming is only eligible for a specific model after its manufacturer documentation or a safely testable, authenticated, writable vendor protocol is verified.

## Evidence

| Finding | Evidence | Confidence |
|---|---|---|
| BLE's advertised local name is an advertisement field, which can be a shortened or complete name. | [Microsoft: `BluetoothLEAdvertisement.LocalName`](https://learn.microsoft.com/en-us/uwp/api/windows.devices.bluetooth.advertisement.bluetoothleadvertisement.localname?view=winrt-28000) | High |
| BLE GAP `Device Name` is a separate GATT characteristic (`0x2A00`); it is *optionally* writable, with permissions defined by a higher-layer spec or implementation. | [Bluetooth SIG Core Spec, GAP §12.1](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-62/out/en/host/generic-access-profile.html) | High |
| A shortened BLE advertised name need not be the full device name; the full name may instead be obtained through BR/EDR remote-name request or GATT after connection. | [Bluetooth SIG CSS, Local Name type](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/CSS_v12/out/en/supplement-to-the-bluetooth-core-specification/data-types-specification.html) | High |
| Windows' advertisement publisher creates an advertisement on behalf of the Windows device, and reserves Local Name advertisement types from apps. It is not a remote-device rename API. | [Microsoft: `BluetoothLEAdvertisementPublisher`](https://learn.microsoft.com/en-us/uwp/api/windows.devices.bluetooth.advertisement.bluetoothleadvertisementpublisher) | High |
| The public Windows `BluetoothDevice` surface supports selecting/querying devices and service access; no documented remote-name setter was identified. | [Microsoft: `BluetoothDevice`](https://learn.microsoft.com/en-us/uwp/api/windows.devices.bluetooth.bluetoothdevice?view=winrt-28000) | Medium-high |

## Required product distinctions

1. **Windows alias / paired-device display name:** OS-local metadata. It does not establish that the earbuds changed their own name.
2. **BLE advertising local name:** ephemeral payload emitted by the earbuds; may be shortened, omitted, or distinct from other names.
3. **BLE GAP Device Name (`0x2A00`):** a remote GATT value. A write is permitted only if the device exposes write property and authorization allows it; a successful write does not prove the advertisement name or nonvolatile firmware state changed.
4. **Classic Bluetooth remote name:** fetched over BR/EDR discovery/remote-name procedures. Its persistence and mutability are controlled by the remote device/firmware.
5. **Firmware/manufacturer state:** the only level that can satisfy the requested independent-rescan acceptance criterion. It must be proven with the relevant model and an independent scanner after a power cycle/reboot as appropriate.

## Design requirements before M3

- Implement discovery/diagnostics first; retain raw/observable evidence (address only when platform supplies one, address type where available, advertisement-local-name presence, RSSI, services, pairing state, and timestamp) with privacy-aware redaction in normal logs.
- Keep BLE and Classic observations separate. Do not infer a shared identity from a display name alone; rotating LE addresses and TWS left/right/case advertisements can make identity ambiguous.
- Make a provider eligible only with a model/firmware matcher, protocol evidence, an explicit compatibility statement, name constraints, authentication requirements, rollback/recovery notes, and an independent verification procedure.
- Treat a writable `0x2A00` as a diagnostic capability, **not** a generic rename provider. It cannot be written blindly, and it cannot be represented as firmware persistence absent rescan evidence.
- UI wording must distinguish: `Windows-only alias`, `observed advertised name`, `unsupported`, `attempt in progress`, `write acknowledged`, and `independently verified`. Never label an acknowledged GATT write as a successful firmware rename.
- Do not send undocumented vendor commands or flash firmware. Never persist pairing keys/credentials. Require an explicit device confirmation before any provider performs a remote write.
- Ensure scanning and every remote I/O action run asynchronously/off the UI thread, with cancellation and bounded timeouts.

## Proposed acceptance gates

| Gate | Required evidence |
|---|---|
| Discovery | Real Windows 11 scan plus mocked tests; clearly label cached/paired data versus current BLE advertisements. |
| Provider enablement | Manufacturer documentation or protocol evidence for the exact model and firmware; no reverse-engineered or destructive procedure without recovery. |
| Rename claim | Provider receipt plus local disconnect/reconnect observation. |
| Final success | A second phone/laptop, with the prior pairing record removed or a fresh scanner, sees the custom name after earbuds power-cycle/reboot. Capture model, firmware, scanner and timestamp in the hardware test record. |

## Environment review

- Workspace was empty at review time (no source, docs, Git repository, or task files present).
- Python available: `3.11.3` (`C:\Users\butem\Desktop\workshop\venv\Scripts\python.exe`).
- PyInstaller command was not found on `PATH`.
- No production files were created or modified by this reviewer, per ownership rules.

## Review finding

| ID | Severity | File | Finding | Suggested resolution |
|---|---|---|---|---|
| M0-001 | Blocker for M3 | Planned firmware provider | Generic remote firmware rename is unsupported by the Bluetooth standards/Windows APIs examined. | Keep M3 blocked until a device-specific, evidenced provider exists; otherwise release diagnostics and an honest unsupported result only. |

