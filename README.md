# TWS Name Changer

Windows 11 desktop diagnostics for Bluetooth earbuds. It discovers nearby BLE devices and shows what Windows observed. It does **not** change the Windows display alias and does not claim a firmware rename for unsupported devices.

## Bluetooth transport limitation

BLE advertising and Windows paired Bluetooth records are collected independently. Bleak does not actively discover Classic BR/EDR devices; the Windows backend only enumerates existing paired records and can be denied by system privacy policy. Thus a Classic-only unpaired device can be absent from the list even when visible in Windows Bluetooth Settings. Paired records are cached system metadata, not proof that a device is currently nearby or advertising.

## Status

Firmware-level renaming is unavailable until a provider has been verified for an exact earbud model and firmware. The included provider registry therefore returns an honest unsupported result.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

See `docs/TESTING.md` for test commands and the independent-device verification checklist.

## Safety

Use only with devices you own or are authorised to administer. The app does not pair, unpair, flash firmware, or send undocumented commands.

