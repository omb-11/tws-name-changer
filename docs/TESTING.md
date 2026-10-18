# Testing

```powershell
.venv\Scripts\python -m pytest
```

Hardware checklist: test with Bluetooth off, no adapter, scan cancel, nearby BLE device, and unsupported earbuds. Confirm a paired Classic headset/earbuds appears as `Windows paired Bluetooth` and not as a live advertisement. If access is denied, inspect Windows Bluetooth/app privacy permissions and record the exact error. Also compare the list against Windows Bluetooth Settings for a known Classic-only unpaired headset/earbuds and record the expected absence. For any future provider, disconnect the earbuds, power-cycle them, remove/avoid cached pairing on a separate phone/laptop, rescan there, and record the observed name plus model, firmware, provider version, timestamp, and scanner. A local Windows result is never sufficient by itself.

