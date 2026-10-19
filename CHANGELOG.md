# Changelog

## [1.0.0] - 2026-10-19

### Added
- **Verified Portable Windows Executable:** Built and verified standalone `dist/TWSNameChanger.exe` (~202 MB) with zero console window and full PySide6/Bleak/WinRT runtime bundling.
- **Modern PySide6 GUI:** Two-column layout with device list, selected-device inspector (name, address, source badge, pairing state, RSSI, advertised services), indeterminate progress bar, scan refresh, and transparent status messages.
- **About & Technical Help Dialog:** Explains live BLE vs. cached Classic records, local Windows aliases vs. firmware broadcast names, and Windows error codes (`0x800710DF`, `0x80070005`).
- **User-Level Storage & Logging:** Configured `%LOCALAPPDATA%\TWSNameChanger` for settings persistence and safe privacy-conscious diagnostic logs.
- **Repeatable Release Pipeline:** Added `build.ps1` automated build script and `verify_exe.py` for headless executable startup validation.
- **Inno Setup Script:** Added `installer/setup.iss` for optional Windows installer creation.
- **Comprehensive Test Suite:** Expanded test suite to 59 automated unit and GUI integration tests.

### Fixed
- **PySide6 Packaging Error:** Resolved `ModuleNotFoundError: No module named 'PySide6'` by properly targeting the project virtual environment and configuring PyInstaller `collect_all` hooks for PySide6, Bleak, and WinRT.
- **WinRT Collection Iteration:** Fixed Windows paired-Classic enumeration by indexing the `DeviceInformationCollection` with `range(len(records))`, eliminating the missing `winrt.windows.foundation.collections` dependency.
- **Synchronous Address Extraction:** Added `_extract_address_from_id` to parse device MAC addresses synchronously from WinRT device IDs, avoiding blocking async lookups.
