# TWS Name Changer

Windows 11 desktop diagnostics for Bluetooth earbuds. It discovers nearby BLE devices and shows what Windows observed. It does **not** change the Windows display alias and does not claim a firmware rename for unsupported devices.

## Bluetooth transport limitation

The current scan is BLE-only. Some TWS products expose audio and discoverability through Bluetooth Classic (BR/EDR), which Bleak does not actively discover. Such devices can be absent from this list even when visible in Windows Bluetooth Settings. This is an honest limitation, not an indication that the earbuds are unsupported for all future diagnostics. A separately tested Windows Classic/paired-device backend is required before claiming Classic discovery support.

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

