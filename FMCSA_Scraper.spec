# THIS CODE IS AI GENERATED
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project_root = Path('.').resolve()

block_cipher = None

# Collect all submodules from your packages
hidden_imports = collect_submodules('utils') + collect_submodules('scrapers')

a = Analysis(
    ['interface.py'],  # Entry point
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include all config files
        (str(project_root / 'config' / 'config.json'), 'config'),
        (str(project_root / 'config' / 'secrets.json'), 'config'),
        # Include Google service account JSON
        (str(project_root / 'sheets-csv-update-[SECRET].json'), '.'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FMCSA_Scraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False because this is a Tkinter GUI
    disable_windowed_traceback=False,
    target_arch=None,
    icon=None  # You can add an .ico file here if you want
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FMCSA_Scraper'
)
