# -*- mode: python ; coding: utf-8 -*-
import os
# SPDX-License-Id: MIT
# Credit: Jack Giffin and platformdirs: github.com/tox-dev/platformdirs
# Source: https://stackoverflow.com/a/79403791/5601591

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[("assets","assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        name='main',
        debug=False,
        strip=False,
        upx=True,
        icon="assets/logo.ico",
        console=False
        )