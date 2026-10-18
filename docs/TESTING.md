# Testing

```powershell
.venv\Scripts\python -m pytest
```

Hardware checklist: test with Bluetooth off, no adapter, scan cancel, nearby BLE device, and unsupported earbuds. Also compare the BLE-only list against Windows Bluetooth Settings for a known Classic-only headset/earbuds and record the expected absence. For any future provider, disconnect the earbuds, power-cycle them, remove/avoid cached pairing on a separate phone/laptop, rescan there, and record the observed name plus model, firmware, provider version, timestamp, and scanner. A local Windows result is never sufficient by itself.

