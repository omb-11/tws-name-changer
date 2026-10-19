# TWS Name Changer — Release Documentation (v1.0.0)

## Overview

**TWS Name Changer** is a Windows 11 desktop diagnostic and Bluetooth discovery tool built with Python 3.11, PySide6, Bleak, and Windows Runtime (WinRT).

This release delivers:
- Verified portable standalone executable: `dist/TWSNameChanger.exe`
- Repeatable automated build pipeline: `build.ps1`
- Inno Setup script for optional installer packaging: `installer/setup.iss`
- Full test suite: 59 automated tests passing with 100% pass rate.

---

## Release Artifacts

| Artifact | Path | Size | Description |
|---|---|---|---|
| **Portable Executable** | `dist\TWSNameChanger.exe` | ~202 MB | Windowed GUI executable (no console window). Self-contained with Python runtime, PySide6, Bleak, and WinRT native extensions. |
| **Build Script** | `build.ps1` | ~3 KB | PowerShell automated pipeline that runs tests, bytecode verification, cleans cache, runs PyInstaller, and tests executable startup. |
| **Inno Setup Script** | `installer\setup.iss` | ~1 KB | Inno Setup configuration for generating `dist\installer\TWSNameChanger-Setup.exe`. |

---

## Technical Architecture & Packaging Fix

### Packaging Root Cause & Resolution
In the previous build, PyInstaller was invoked using a global Python environment where `PySide6` and `winrt` were not installed, resulting in `ModuleNotFoundError: No module named 'PySide6'` at runtime.

The release pipeline now:
1. Operates strictly within the project virtual environment (`.venv\Scripts\python.exe`).
2. Configures `TWSNameChanger.spec` with `pathex=['src', '.']` and explicit `collect_all` hooks for `PySide6`, `bleak`, and `winrt`.
3. Handles both frozen (`sys._MEIPASS`) and development runtimes seamlessly in `main.py`.
4. Executes automated verification (`verify_exe.py`) confirming the packaged executable launches stably and displays the UI.

---

## Hardware Verification & Discovery Results

### Tested on Real Windows 11 Hardware (Intel Bluetooth Adapter)

| Component | Hardware Test Result | Details |
|---|---|---|
| **BLE Discovery (`BleakDiscoveryBackend`)** | ✅ **VERIFIED ON HARDWARE** | Scanned nearby BLE devices via Windows BLE Advertisement Watcher. Successfully discovered between 8 and 18 live nearby devices. |
| **Paired Classic Discovery (`WindowsPairedClassicBackend`)** | ✅ **VERIFIED ON HARDWARE** | Successfully queried WinRT `BluetoothDevice.get_device_selector()` and indexed `DeviceInformationCollection`. Successfully identified 2 cached `pTron TWS` records and extracted MAC addresses synchronously (`4142FF85AA71` and `595C22EC8909`). |
| **Unified Merger (`UnifiedDiscoveryBackend`)** | ✅ **VERIFIED ON HARDWARE** | Concurrently aggregated live BLE devices and cached Windows Classic records without loss or false deduplication. |
| **Adapter Error Handling** | ✅ **VERIFIED** | Actionable diagnostic messages provided for `0x800710DF` (Bluetooth disabled or service stopped) and `0x80070005` (Windows privacy permission blocked). |

---

## Firmware Renaming Assessment

### Objective
Change the persistent advertised Bluetooth name broadcast by pTron TWS earbuds to external devices (phones, tablets, other laptops).

### Findings & Truthful Status
- **Local Windows Alias vs. Firmware Broadcast:** Renaming a device in Windows Settings alters a local registry display alias on that specific PC only. It does **not** change what the earbuds broadcast over the air.
- **Hardware Architecture:** Low-cost TWS earbuds (such as pTron, Boat, Noise, using JL JieLi AC69xx, Actions ATS301x, or Realtek chipsets) store their broadcast name in internal Flash/NVRAM. Modifying this requires vendor-proprietary Over-The-Air (OTA) flashing commands or vendor factory tools.
- **Safety & Integrity:** Arbitrary GATT or SPP command transmission without manufacturer documentation risks bricking the earbuds or corrupting Bluetooth MAC addresses.
- **Application Behavior:** The application explicitly labels renaming as **Unsupported** for unverified devices. No unauthorized or destructive commands are sent.

---

## How to Run & Verify

### Running the Packaged Executable
Double-click `dist\TWSNameChanger.exe` or execute from PowerShell:
```powershell
.\dist\TWSNameChanger.exe
```

### Running Automated Verification
```powershell
.venv\Scripts\python verify_exe.py
```

### Running the Full Build Pipeline
```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```
