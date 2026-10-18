# Firmware-renaming feasibility

## Conclusion

There is no standard Windows or Bluetooth operation that changes a remote earbud's persistent advertised name. Windows may display a local paired-device alias; this is not a firmware rename. This project deliberately has no generic remote-write provider.

BLE advertising can include a shortened or complete local name. Separately, the GAP Device Name characteristic (`0x2A00`) may be writable, but the Bluetooth specification makes writes optional and implementation-specific. A write acknowledgement does not prove advertising or persistent firmware state changed. Classic Bluetooth remote names are likewise controlled by the remote firmware.

## Discovery transport limitation

`BleakDiscoveryBackend` performs live BLE advertisement discovery only. `WindowsPairedClassicBackend` uses the supported `Windows.Devices.Bluetooth.BluetoothDevice` selector with `Windows.Devices.Enumeration.DeviceInformation` to enumerate paired Bluetooth records. It is **not** a live BR/EDR inquiry. Many earbuds use a BLE control channel in addition to Classic audio, while others are discoverable only through Classic Bluetooth. An absent device is not proof that it is absent, unpaired, or incompatible. The UI labels source and transport separately, and never treats a paired record as live advertising.

## Provider admission requirements

A provider requires all of: exact model and firmware matcher; official manufacturer documentation or equivalent safe protocol evidence; authenticated command constraints; maximum UTF-8 byte length; recovery/rollback procedure; local reconnect observation; and independent phone/laptop scan after a power cycle. Unsupported hardware must say so.

## Sources

- [Bluetooth SIG GAP Device Name](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-62/out/en/host/generic-access-profile.html)
- [Bluetooth SIG Local Name data type](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/CSS_v12/out/en/supplement-to-the-bluetooth-core-specification/data-types-specification.html)
- [Microsoft BLE advertisement watcher](https://learn.microsoft.com/en-us/uwp/api/windows.devices.bluetooth.advertisement.bluetoothleadvertisementwatcher)

