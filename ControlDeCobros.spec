# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

webengine_datas, webengine_binaries, webengine_hiddenimports = collect_all(
    "PySide6.QtWebEngineCore"
)

a = Analysis(
    ['app\\main.py'],
    pathex=[],
    binaries=webengine_binaries,
    datas=[('ui', 'ui')] + webengine_datas,
    hiddenimports=webengine_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='ControlDeCobros',
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
