# -*- mode: python ; coding: utf-8 -*-
import shutil, os

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('devices/TS001.json',          'devices')
        , ('devices/TS001.json',        'devices')
        , ('devices/TC001.json',        'devices')
        , ('devices/TC001tariq.json',   'devices') 
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='ptc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory='bin',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pythermalcamera',
)

# Move files
dist_dir = os.path.join(DISTPATH, 'main')
src = os.path.join(dist_dir, 'bin', 'devices')
dst = os.path.join(dist_dir, 'devices')
if os.path.exists(src):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.move(src, dst)
