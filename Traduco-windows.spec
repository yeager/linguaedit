# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Windows build (run on Windows or via GitHub Actions)

a = Analysis(
    ['src/traduco/app.py'],
    pathex=['src'],
    binaries=[],
    datas=[('po/locale', 'locale')],
    hiddenimports=['traduco'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['enchant', 'pyenchant'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Traduco',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='data/traduco.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='Traduco',
)
