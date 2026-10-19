# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules

datas_winrt, binaries_winrt, hiddenimports_winrt = collect_all('winrt')
datas_bleak, binaries_bleak, hiddenimports_bleak = collect_all('bleak')
datas_pyside6, binaries_pyside6, hiddenimports_pyside6 = collect_all('PySide6')

datas = [('src', 'src')] + datas_winrt + datas_bleak + datas_pyside6
binaries = binaries_winrt + binaries_bleak + binaries_pyside6
hiddenimports = (
    hiddenimports_winrt
    + hiddenimports_bleak
    + hiddenimports_pyside6
    + [
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'bleak',
        'bleak.backends.winrt',
        'winrt',
        'winrt.windows.foundation',
        'winrt.windows.devices.bluetooth',
        'winrt.windows.devices.enumeration',
        'tws_name_changer',
        'tws_name_changer.app',
        'tws_name_changer.bluetooth.base',
        'tws_name_changer.bluetooth.device_info',
        'tws_name_changer.bluetooth.discovery',
        'tws_name_changer.bluetooth.providers.unsupported',
        'tws_name_changer.services.rename_service',
        'tws_name_changer.services.verification',
        'tws_name_changer.storage.settings',
        'tws_name_changer.ui.main_window',
        'tws_name_changer.utils.logging_config',
    ]
)

a = Analysis(
    ['main.py'],
    pathex=['src', '.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TWSNameChanger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
