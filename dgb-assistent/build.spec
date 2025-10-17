# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Get the source directory
src_dir = os.path.join(os.getcwd(), 'src')

a = Analysis(
    [os.path.join(src_dir, 'main.py')],
    pathex=[src_dir],
    binaries=[],
    datas=[
        (os.path.join(src_dir, 'assets'), 'assets'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'requests',
        'csv',
        'pathlib',
        'threading',
        'tempfile',
        'apps.image_tools.simple_resizer',
        'apps.image_tools.group_processor',
        'apps.image_tools.individual_processor',
        'apps.image_tools.museum_organizer',
        'utils.sara_uploader',
        'utils.settings',
        'utils.helpers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas', 
        'altair',
        'streamlit',
        'Django',
        'Flask',
        'selenium',
        'webdriver_manager',
        'google-generativeai',
        'google-cloud-vision',
        'openai',
        'GitPython',
        'unicorn',
        'helper',
        'image',
        'xlsxwriter',
        'openpyxl',
        'pyarrow',
        'pydeck',
        'test',
        'tests',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DGB-Assistent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)