# M0 security, privacy, and release-gate review

**Reviewer:** OpenAI Codex  
**Date:** 2026-10-18  
**Review state:** No production source exists yet. These are mandatory criteria for implementation and later audit.

## Security posture

The application must operate as a local, user-directed Bluetooth diagnostic/rename client. It should neither attempt pairing, unpairing, credential extraction, firmware flashing, nor arbitrary vendor-command replay. The normal path needs no administrator privilege, network service, cloud account, telemetry, or background operation.

### Required controls

| Area | Requirement | Verification evidence |
|---|---|---|
| Remote writes | A rename control is enabled only after the selected provider's exact model/firmware preflight succeeds. Require an explicit confirmation showing provider ID, expected outcome, and known risks. | Unit/UI tests plus a provider-specific hardware record. |
| Input | Reject empty/whitespace-only names, control characters, invalid Unicode/surrogates, and names exceeding the provider's verified byte limit. Measure UTF-8 bytes, not Python character count. | Boundary and Unicode tests. |
| Protocol safety | Providers must build only documented, bounded requests. No user-entered payload, address, UUID, or raw command may flow into a Bluetooth write. | Code review and tests. |
| Timeouts | Bound discovery, connection, service enumeration, write, disconnect, and verification; provide cancellation. | Fake-backend timeout tests. |
| Pairing state | Do not trigger pairing/unpairing or store pairing secrets. If Windows requires a pre-existing paired connection, instruct the user and stop. | Code search/audit; manual test. |
| Privilege | Do not elevate, edit registry Bluetooth keys, or use driver/kernel tooling. | Packaging manifest and source audit. |
| Dependencies | Pin dependencies, run vulnerability review before release, and record Python/PySide6/WinRT/BLE backend/PyInstaller versions used for the build. | Lock/report and CI output. |
| Logs | Never log pairing keys, raw manufacturer payloads by default, or full Bluetooth addresses. Use a per-run salted/short display ID and allow a deliberate diagnostics export with a warning. | Log unit tests and manual inspection. |
| Persistence | Settings may contain UI preferences and opt-in known-device labels only. Make device metadata retention explicit and deletable. Use an application-data directory with restrictive normal-user permissions; no secrets. | Settings tests and filesystem audit. |
| Error messages | Explain failures without falsely assigning fault or leaking unnecessary identifiers. Do not reveal raw exception traces in the default UI. | Error mapping tests. |

## Threat and misuse boundaries

| Scenario | Expected behavior |
|---|---|
| Unknown earbuds or a device that merely resembles a supported device | Report unsupported; never probe writable GATT characteristics or vendor endpoints speculatively. |
| Malicious BLE advertisement / malformed name | Treat all remote fields as untrusted; sanitize for UI/logging, cap lengths, and do not use display text as an identifier or file path. |
| Address rotation / nearby look-alike device | Require multiple matching, non-sensitive observations and report ambiguity; do not direct a write on an inferred identity. |
| Device disconnects mid-operation | Stop safely; report outcome as unknown/not verified; never retry a remote write automatically. |
| User tries a custom name containing confusable/control content | Show the sanitized preview and reject controls; optionally warn about leading/trailing whitespace and visually confusable labels. |
| Provider implementation is undocumented or recovery is unknown | Exclude it from the release; document the device as unsupported. |

## Release claims: allowed wording

| State | Permitted UI/documentation wording | Prohibited wording |
|---|---|---|
| No matching provider | “Firmware name change is not supported for this device.” | “Rename failed” (unless an attempt occurred), “Windows renamed it.” |
| Provider acknowledged remote request | “The device acknowledged a provider-specific request. Persistence has not been verified.” | “Renamed successfully.” |
| Local re-observation matches | “Observed locally after reconnect; verify on a separate scanner.” | “Firmware rename verified.” |
| Separate scanner and power-cycle evidence captured | “Independently verified for [exact model/firmware/provider version].” | “Works for all TWS earbuds.” |

## Release gate checklist

- [ ] `docs/FEASIBILITY.md` cites a primary/official source for every supported provider and lists model/firmware scope, recovery information, and unresolved questions.
- [ ] Provider registry has no generic “GAP device name writer,” Windows-alias writer, raw-command console, or hidden experimental provider in release builds.
- [ ] The GUI visibly distinguishes current advertising observation, paired/cached record, local verification, and independent verification.
- [ ] Automated tests pass in a clean Python 3.11+ environment.
- [ ] Hardware tests cover adapter unavailable, scan cancellation, unsupported earbuds, and each claimed supported model/firmware.
- [ ] Independent verifier evidence includes scanner type/version, prior-pairing state, power-cycle/reboot state, observed name, date, exact firmware, and application/provider version.
- [ ] A clean Windows 11 profile has launched the packaged executable and scanned successfully without admin rights.
- [ ] Third-party licenses, dependency notices, and build hash/version are included with the release.
- [ ] Normal logs/settings were inspected for Bluetooth addresses, personal names, payloads, and credentials.

## Findings

| ID | Severity | Planned area | Suggested resolution |
|---|---|---|---|
| M0-006 | Critical | Rename provider design | Make exact compatibility preflight and explicit confirmation non-bypassable; prohibit generic writable-GATT fallback. |
| M0-007 | High | Logging/storage | Define redaction/retention rules before implementing diagnostics; test them. |
| M0-008 | High | Release documentation | Gate all success claims on independent-scanner, post-power-cycle evidence for the exact model/firmware. |
| M0-009 | Medium | UI/input | Validate a provider-specific UTF-8 byte limit and prevent UI/log injection via remote or entered names. |

