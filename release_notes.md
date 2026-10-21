# TWS Name Changer v1.0.0 — Windows 11 Desktop Diagnostics

**TWS Name Changer** is an honest, transparent diagnostic utility for Bluetooth earbuds on Windows 11 and Windows 10 (64-bit).

---

## 🚀 Release Highlights

- **Verified Standalone Executable:** Includes `TWSNameChanger.exe` (~202 MB), bundled with Python 3.11, PySide6, Bleak, and native Windows Runtime (WinRT) components. No Python environment, external libraries, or administrator privileges required.
- **Concurrent Dual-Source Discovery:**
  - **Live BLE Discovery:** Utilizes Windows BLE Advertisement Watcher to detect active over-the-air broadcasts from nearby devices, capturing signal strength (RSSI) and service UUIDs.
  - **Windows Paired Classic Enumeration:** Queries the native WinRT device registry to identify paired Bluetooth Classic (BR/EDR) records even when devices are temporarily disconnected or in case.
- **Strict Source Differentiation:** Visual indicators (`[BLE Live]` vs. `[Windows Paired]`) prevent confusing cached offline records with active nearby broadcasts.
- **Selected Device Inspector:** Displays clean device name, MAC address, transport type, pairing state, RSSI, advertised services, and rename capability.
- **Hardware-Safe Truthfulness:** Clearly distinguishes between local Windows display aliases (which only change names on this PC) and genuine firmware broadcasts. Unsupported devices (such as pTron TWS) are protected against dangerous, undocumented write attempts.
- **Actionable Win32 Diagnostics:** Built-in guidance for Windows Bluetooth error codes `0x800710DF` (Bluetooth disabled/service stopped) and `0x80070005` (Privacy Bluetooth permissions blocked).

---

## 📦 Assets & Verification

- **Live Download Website:** [https://website-gamma-flax-47.vercel.app](https://website-gamma-flax-47.vercel.app)
- **GitHub Release Page:** [https://github.com/omb-11/tws-name-changer/releases/tag/v1.0.0](https://github.com/omb-11/tws-name-changer/releases/tag/v1.0.0)

| Asset | Description | Size |
|---|---|---|
| **`TWSNameChanger.exe`** | Standalone Portable Windows 64-bit GUI Executable | ~202 MB (211,768,830 bytes) |
| **`TWSNameChanger.exe.sha256`** | SHA-256 Checksum Verification File | 96 bytes |

### SHA-256 Checksum
```
339B7F0C4A3972C17456F48BFCCE625D990085BE9CCDBE9A8D5581D1314814BD
```

### Verification Command (PowerShell)
```powershell
Get-FileHash -Path TWSNameChanger.exe -Algorithm SHA256
```

---

## ⚙️ System Requirements
- **Operating System:** Windows 11 (build 22000+) or Windows 10 (64-bit)
- **Hardware:** Intel, Realtek, Qualcomm, or compatible Bluetooth 4.0+ adapter (Classic BR/EDR + BLE support)
- **Permissions:** Standard user account (Administrator privileges NOT required)

---

## ⚠️ Important Limitations & Ethical Disclosure
1. **Firmware Renaming:** Budget TWS earbuds (including pTron, Boat, Noise, based on Actions ATS3015 or JL JieLi chipsets) store their broadcast name in non-volatile flash memory. Modifying the broadcast name observed by other phones or laptops requires proprietary manufacturer OTA flashing protocols. The app will **not** pretend to rename your hardware by creating a local Windows display alias.
2. **Code Signing:** This community open-source binary is self-built without a costly commercial EV code signing certificate. Windows SmartScreen may show an informational prompt on first run ("Windows protected your PC"). Click *More info* -> *Run anyway* to launch.
