# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/amherst/shipper.py'],
    pathex=['.'],
    binaries=[],
    datas=[
         ('src/amherst/front/static', 'front/static'),
         ('src/amherst/front/templates', 'front/templates'),
    ],
    hiddenimports=['ipaddress', 'pyinstaller.importers'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)



pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='shipper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
