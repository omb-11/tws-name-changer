# Final QA Audit Report — TWS Name Changer v1.0.0

**Date:** 2026-10-19  
**Platform:** Windows 11 (x64)  
**Python Runtime:** Python 3.11.3 (in `.venv`)  
**Status:** PASS / RELEASE VERIFIED  

---

## 1. Executive Summary

A full bug hunt and release verification was performed following the previous broken PyInstaller release (`ModuleNotFoundError: No module named 'PySide6'`).

The root cause was identified and remediated: PyInstaller was previously executed in an unconfigured global Python environment rather than the project virtual environment. The build pipeline was rebuilt from the ground up:
- PyInstaller is now invoked strictly within `.venv`.
- `TWSNameChanger.spec` collects PySide6, Bleak, and WinRT native runtime packages.
- `main.py` supports both frozen execution (`sys._MEIPASS`) and development checkout.
- The compiled executable `dist/TWSNameChanger.exe` (201.96 MB) was launched and verified to run stably without crashing or throwing import errors.
- 59 automated unit and GUI integration tests pass (100% success rate).
- Both BLE and Windows Classic Bluetooth discovery were validated on actual local Windows 11 hardware with an Intel Bluetooth adapter.

---

## 2. Test Execution & Coverage Summary

| Test Module | Tests | Result | Notes |
|---|---|---|---|
| `tests/test_discovery.py` | 41 | **PASSED** | Name cleaning, WinRT ID address extraction, error diagnostics, mock backends, unified merger. |
| `tests/test_gui.py` | 5 | **PASSED** | Offscreen Qt testing for `MainWindow`, device selection, details display, rename request, `AboutDialog`. |
| `tests/test_rename_service.py` | 5 | **PASSED** | Unsupported device protection, invalid name checks, UTF-8 GAP length limits. |
| `tests/test_settings.py` | 6 | **PASSED** | AppData directory resolution, default paths, JSON load/save, corrupt file resilience. |
| `tests/test_verification.py` | 2 | **PASSED** | Local observation matching, independent verification boundaries. |
| **Total Test Suite** | **59** | **ALL PASSED** | Execution time: ~1.2s |

---

## 3. Packaged Executable Verification

- **Executable:** `C:\Users\butem\Desktop\tws-name-changer\dist\TWSNameChanger.exe`
- **File Size:** 211,768,830 bytes (201.96 MB)
- **Startup Test (`verify_exe.py`):**
  * Process launched (PID 31092).
  * Main event loop initialized cleanly.
  * No `ModuleNotFoundError` or uncaught exceptions.
  * Memory and thread handles remained healthy.
  * Process exited cleanly upon termination request.

---

## 4. Hardware Verification Breakdown

1. **Windows Paired Classic Backend:**
   - Evaluated using WinRT `DeviceInformation.find_all_async_aqs_filter(selector)` on real Intel adapter.
   - Discovered 2 cached `pTron TWS` records.
   - Synchronous address parsing successfully retrieved addresses `4142FF85AA71` and `595C22EC8909` without network/connection roundtrips.
   - Correctly flagged pairing state as `paired=False` (retained in Windows AEP cache).

2. **Bleak BLE Discovery Backend:**
   - Evaluated using Windows BLE Advertisement Watcher on real Intel adapter.
   - Live hardware scan successfully discovered nearby BLE devices (8 to 18 devices discovered depending on radio traffic).

3. **Unified Discovery Aggregation:**
   - Concurrent execution aggregated live BLE devices with cached Windows Classic records.
   - Results correctly differentiated in the UI with source badges `[BLE Live]` vs. `[Windows Paired]`.

---

## 5. Firmware Renaming & Ethical Transparency

- Firmware renaming for pTron TWS earbuds is explicitly reported as **Unsupported**.
- The UI prevents deceptive claims: changing a local Windows alias does not modify the over-the-air broadcast name.
- No dangerous or undocumented brute-force commands are sent to physical hardware.
