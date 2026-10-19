# TWS Name Changer

Windows 11 desktop application and diagnostics for Bluetooth earbuds. It discovers nearby BLE advertisements and enumerates Windows paired Bluetooth records without claiming unverified firmware renaming capabilities.

---

## Features

- **Live BLE Discovery:** Discovers nearby BLE devices using Bleak and Windows BLE Advertisement Watcher.
- **Windows Paired Classic Enumeration:** Enumerates cached/paired Bluetooth Classic devices using Windows WinRT APIs without requiring administrative privileges.
- **Source Differentiation:** Distinct badges and detailed metadata (`[BLE Live]` vs `[Windows Paired]`) so cached records are never confused with live nearby broadcasts.
- **Selected Device Inspector:** Displays device name, MAC address, transport, pairing status, signal strength (RSSI), and advertised services.
- **Honest Diagnostics:** Clearly reports firmware renaming as unsupported for devices lacking verified manufacturer protocols. Does not deceive by changing local Windows display aliases.
- **Robust Packaging:** Self-contained, portable Windows executable (`dist/TWSNameChanger.exe`) with PySide6, Bleak, and WinRT bundled.

---

## Running the Standalone Executable

No Python installation required. Simply launch:
```powershell
.\dist\TWSNameChanger.exe
```

---

## Development Setup

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

### Running Tests
```powershell
.venv\Scripts\python -m pytest -v
```

### Running the Build Pipeline
```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

---

## Bluetooth Transport Limitations

BLE advertising and Windows paired Bluetooth records are collected independently. Bleak does not actively discover Classic BR/EDR devices; the Windows backend only enumerates existing paired records and can be denied by system privacy policy. Thus a Classic-only unpaired device can be absent from the list even when visible in Windows Bluetooth Settings. Paired records are cached system metadata, not proof that a device is currently nearby or advertising.

---

## Safety

Use only with devices you own or are authorised to administer. The app does not pair, unpair, flash firmware, or send undocumented commands.
