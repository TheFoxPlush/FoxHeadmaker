# -*- mode: python ; coding: utf-8 -*-
import os
# SPDX-License-Id: MIT
# Credit: Jack Giffin and platformdirs: github.com/tox-dev/platformdirs
# Source: https://stackoverflow.com/a/79403791/5601591
def user_cache_dir_from_platformdirs():
    from sys import platform, path
    from os import getenv, path
    if platform == "darwin":
        return os.path.expanduser("~/Library/Caches")
    elif platform == "win32":
        try: # https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid
            from ctypes import windll, wintypes, create_unicode_buffer, c_int
            buf, gfpW = create_unicode_buffer(1024), windll.shell32.SHGetFolderPathW
            gfpW.argtypes = [wintypes.HWND,c_int,wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR]
            gfpW.restype = wintypes.HRESULT
            if 0 == gfpW(None, 28, None, 0, buf) and buf[0] != 0:
                return buf.value # CSIDL_LOCAL_APPDATA = 28
        except Exception:
            pass
        if getenv("LOCALAPPDATA") and path.isdir(getenv("LOCALAPPDATA")):
            return getenv("LOCALAPPDATA")
        from winreg import OpenKey, QueryValueEx, HKEY_CURRENT_USER
        key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        return str( QueryValueEx(key, "Local AppData")[1] )
    # For all Linux and *nix including Haiku, OpenIndiana, and the BSDs:
    return getenv("XDG_CACHE_HOME","").strip() or path.expanduser("~/.cache")

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
        runtime_tmpdir=user_cache_dir_from_platformdirs(),
        icon="assets/logo.ico",
        console=False
        )