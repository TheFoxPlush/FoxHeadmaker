from tkinter import IntVar, StringVar, BooleanVar, PhotoImage, filedialog, Canvas, Tk, Toplevel, TclError
from tkinter import Frame as tk_Frame
from tkinter import Label as tk_Label
from tkinter.ttk import Notebook, Frame, Button, Label, Entry, Checkbutton, Scrollbar, Style
import webbrowser
import os
import sys
from pathlib import Path
if sys.platform == "win32":
    from pywinstyles import change_header_color as pywinstyles_change_header_color
    from pywinstyles import apply_style as pywinstyles_apply_style
from math import floor
from sv_ttk import set_theme, get_theme
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageTk
from threading import Thread
from requests import post as requests_post
from requests import get as requests_get
from time import sleep, time, monotonic
from io import BytesIO
from json import load as json_load
from json import dump as json_dump
from json import loads as json_loads
from json import dumps as json_dumps
from pyperclip import copy as pyperclip_copy
from websockets.sync.client import connect
from base64 import b64decode, b64encode
from darkdetect import theme as darkdetect_theme
from packaging import version
import logging
from playsound3 import playsound


def asset(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

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

__version__ = "2.0.0"

LATEST_URL_API = "https://api.github.com/repos/TheFoxPlush/FoxHeadmaker/releases/latest"
LATEST_URL = "https://github.com/TheFoxPlush/FoxHeadmaker/releases/latest"

CACHE_DIR = os.path.join(user_cache_dir_from_platformdirs(),"FoxHeadmaker")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def _cache_folders(folders):
    dirs = []
    for folder in folders:
        dir_ = os.path.join(CACHE_DIR,folder)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        dirs.append(dir_)
    return dirs

CRASH_REPORTS_DIR = _cache_folders(["crash_reports"])

HOME_DIR = os.path.expanduser("~/Desktop")

CONFIG_PATH = os.path.join(CACHE_DIR,"config.json")
if not(os.path.isfile(CONFIG_PATH)):
    with open(CONFIG_PATH,"w") as configfile:
        json_dump({},configfile)

LOG_PATH = os.path.join(CACHE_DIR,"errors.log")
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)

HEAD_ID_CACHE_PATH = os.path.join(CACHE_DIR,"head_id_cache.json")
if not(os.path.isfile(HEAD_ID_CACHE_PATH)):
    with open(HEAD_ID_CACHE_PATH,"w") as headidcachefile:
        json_dump({},headidcachefile)

HEAD_TEMPLATE = Image.open(BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00@\x00\x00\x00@\x02\x03\x00\x00\x00\xd7\x07\x99M\x00\x00\x00\tPLTE\x00\x00\x00 \x018\xff\xfc\xfdI\xad\x01\xf5\x00\x00\x00\x01tRNS\x00@\xe6\xd8f\x00\x00\x01UIDATx\x9c\xc5R\xc1J\xc3@\x14\x9c\xdd\xec\x9e\xd2B\xa0\xf1;L\x0f\x1e\xc5\x15z\xec!`r\xf0\x1b\xfc\xb4(\xb4\x90\xa3\x87-\xe8Mi\xff\xc3\x06\x025\xa74<\xd9\xddD\xd3PE\x11\xf4A\xd8e\xf6\xedd\xde\xec0 \x05\x90\xa1+\xfe\xbe\xfbS\x80\x19\x15\xe8)\xe1\xff\xa3\x83g@f4\xa4@\x9a\xfer\x16W\xd9\x91+\t\xc4\x0c\x80\xe8\x00Q\x04\x11C0\xa5pY\xbb\x8e\t\x04\x01\xdeC\xe1+\x07\x14vi>8`\x8b\x14\xaa\x16\x98ThPI\rG\xd1\xd3!\xeb\x81\x8e\xb6\xe3\x93Y\xd2\xa1\x1f/R\x08\xe3J\xd6u\x84\xfe\xf9\xe8\xe0\xca\x16\x14\x1d\n\x03\xdbt\x1b\xcb\xa7\x1e\t{\xe7\x87\x1b[\x0f\x7f\xdb+\x8e@\x01\xac\xb5H\xd9\x0e\xa6b\x9c$\x12A\xec\xac\x93\xde\xd3kX\x17\xf5\xac\xc9\xe7\xa5\x01j\xa6D\xb1\x86d\xfaj\xebHi\xb9\x00\xe0\x93\xba5\xa4\x02h.\xc2\x15Pa\x1d\x97z\xf8P\xeaf\xa0C\x1f\x11\x06\x9b\x8a\xde\xc7\x87\xe7?\xce\xc7\xb72\xc6\x12\x99(\xc8\x18\x90\x97f\x12\xe1\xdd\xd1\x16\x92\x16q)\x9e\x83\xa9w/F\xaaD\xe8\x9f\xed\xf3\xf1n\x0co\xa58\xcb\x81B\x92\xc6\x8eEhh\xe3Hk\r\x8cI\x9b\xdcp\x8aa\xcc\xa0\xf9\xa9\xb2\xb9a\xd7\xac\rF[\xc2>\xd8W\xc2\xde\x00W\xd7h\x14\xb7\xeb\x99\x82\x00\x00\x00\x00IEND\xaeB`\x82')).convert("RGBA")

MIN_REQ_TIME = 4

FUNCTION_ITEM = '''player_head[custom_data={PublicBukkitValues:{"hypercube:codetemplatedata":'{"author":"TheFoxPlush","name":"&b&lFunction &3» &bfoxheadmaker_export","version":1,"code":"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"}'}},custom_name={extra:[{color:"#FFA200",shadow_color:-10341322,text:"FoxHeadmaker Extraction Function"}],italic:0b,text:""},lore=[{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Length: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"16 Blocks",underlined:0b}],text:""},{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Author: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"TheFoxPlush",underlined:0b}],text:""}],profile={id:[I;-1551409397,-611758825,-1137461988,998522893],name:"TheFoxPlush",properties:[{name:"textures",value:"ewogICJ0aW1lc3RhbXAiIDogMTc3Mzk0MzMxMDU5NSwKICAicHJvZmlsZUlkIiA6ICJhMzg3NWYwYmRiODk0ZDE3YmMzM2I1MWMzYjg0NDAwZCIsCiAgInByb2ZpbGVOYW1lIiA6ICJUaGVGb3hQbHVzaCIsCiAgInNpZ25hdHVyZVJlcXVpcmVkIiA6IHRydWUsCiAgInRleHR1cmVzIiA6IHsKICAgICJTS0lOIiA6IHsKICAgICAgInVybCIgOiAiaHR0cDovL3RleHR1cmVzLm1pbmVjcmFmdC5uZXQvdGV4dHVyZS9kMWQ1Nzg3NTFhYzRkMjEzOWY4ODA3ZWE1NWM1MmNhM2ZhYTM3Y2M0NGU3NmMwOTBjMWYzOWZhNDA2NTQ2NzgxIiwKICAgICAgIm1ldGFkYXRhIiA6IHsKICAgICAgICAibW9kZWwiIDogInNsaW0iCiAgICAgIH0KICAgIH0sCiAgICAiQ0FQRSIgOiB7CiAgICAgICJ1cmwiIDogImh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMjhkZTRhODE2ODhhZDE4YjQ5ZTczNWEyNzNlMDg2YzE4ZjFlMzk2Njk1NjEyM2NjYjU3NDAzNGMwNmY1ZDMzNiIKICAgIH0KICB9Cn0="}]}]'''
FUNCTION_ITEM_EXPORTS = '''{DF_NBT:4671,components:{"minecraft:custom_data":{PublicBukkitValues:{"hypercube:codetemplatedata":'{"author":"TheFoxPlush","name":"&b&lFunction &3» &bfoxheadmaker_export","version":1,"code":"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"}'}},"minecraft:custom_name":{extra:[{color:"#FFA200",shadow_color:-10341322,text:"FoxHeadmaker Extraction Function"}],italic:0b,text:""},"minecraft:lore":[{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Length: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"16 Blocks",underlined:0b}],text:""},{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Author: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"TheFoxPlush",underlined:0b}],text:""}],"minecraft:profile":{id:[I;-1551409397,-611758825,-1137461988,998522893],name:"TheFoxPlush",properties:[{name:"textures",signature:"qDqWbVRbv2hK3ik8wfBaIq9icU4qQstuxPfumbSjIv2votLAwmAyhV33I6GRd6gBoEBVyc6Kd3Q8226oj+dJFJ+A7LpDNbrbZbCM9v9dpqeXaInGvMeSq1177roqo0OtgqXt9K9iZ00JVyIPMyzUsN4Ky5LvamXR7YflFmMaPwfpyvBTgTWj2zm6GZ0Oh47BFfHSyKdUEjHnLdE+7vL5/g19C3e/hMkJvC8oUM/cnMuHs6QYBplXOV0bHAD62kdLLsNkTrtVcTyRcX2MfiuyWIe/PGNbul2VDlT32s0XBVWXcomyJ+5MI+X2DXE0nVsMwcDt8kJ4ovbK8qjlCPPSXBSpSZppyMGRLvSOGgQVYbDWyHWkctM6i+eJA5eGeZzqpbHAouxMj4xSO9HzPn4EmDVE8TsOdX9RQNGpfxlnvdU7hlfh7W7NRjnK7YWztVPhMH4QHLIrY+DVvuXKVGrtGr36pezhr/2JSxZ6WgZYofuZ0aE1ejObQiOw8MCNLkLrCC/dZJoOkpAuhTRHqs4Q5PlPwZzK+rIBc34KPhn54f4aUI6oRJPWVr8Hyrv5XpAwboByb/Yj9A7ZH89hZ1lJNfxATJQs1NvLr5N135h1cyefM4Ojsgvu9FqCZ5Vj3VxDYaBfLhIMzckTi8g9lZK1vZzSOeXInf4FD7T9uL0ot8A=",value:"ewogICJ0aW1lc3RhbXAiIDogMTc3Mzk0MzMxMDU5NSwKICAicHJvZmlsZUlkIiA6ICJhMzg3NWYwYmRiODk0ZDE3YmMzM2I1MWMzYjg0NDAwZCIsCiAgInByb2ZpbGVOYW1lIiA6ICJUaGVGb3hQbHVzaCIsCiAgInNpZ25hdHVyZVJlcXVpcmVkIiA6IHRydWUsCiAgInRleHR1cmVzIiA6IHsKICAgICJTS0lOIiA6IHsKICAgICAgInVybCIgOiAiaHR0cDovL3RleHR1cmVzLm1pbmVjcmFmdC5uZXQvdGV4dHVyZS9kMWQ1Nzg3NTFhYzRkMjEzOWY4ODA3ZWE1NWM1MmNhM2ZhYTM3Y2M0NGU3NmMwOTBjMWYzOWZhNDA2NTQ2NzgxIiwKICAgICAgIm1ldGFkYXRhIiA6IHsKICAgICAgICAibW9kZWwiIDogInNsaW0iCiAgICAgIH0KICAgIH0sCiAgICAiQ0FQRSIgOiB7CiAgICAgICJ1cmwiIDogImh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMjhkZTRhODE2ODhhZDE4YjQ5ZTczNWEyNzNlMDg2YzE4ZjFlMzk2Njk1NjEyM2NjYjU3NDAzNGMwNmY1ZDMzNiIKICAgIH0KICB9Cn0="}]}},count:1,id:"minecraft:player_head"}'''

LORE_TINT = Image.new("RGBA",(8,8),(170,0,170,255))

SHADOW_TINT = Image.new("RGBA",(8,8),(64,64,64,255))

MINECRAFT_FONT = ImageFont.truetype(asset(os.path.join("assets","Minecraft.otf")), 9)

ITEM_APPLE_IMAGE = Image.open(asset(os.path.join("assets","items","apple.png")))

EXTRACTION_FUNCTION_ITEM_FORMATS = {
    "give":'''player_head[custom_data={PublicBukkitValues:{"hypercube:codetemplatedata":'{"author":"TheFoxPlush","name":"&b&lFunction &3» &bfoxheadmaker_export","version":1,"code":"H4sIAAAAAAAA/8VXa5OiSBb9K4QbGzETWiugKLrRH5CH+AAVkdd0R0XyUJCnPFTo6P++iVpdVtdMTW3XduwHQ7h57817Tt7Mk3xtmEFs+Vlj+MfXhmc3htf3Ruv2P2xsi8iCryDdQSfokzvhzRs+XSx11OWl1bBBDp68oPUrwz2KI3nY7fWxlhWHSRw5UZ4Nv35uhF7kWCnY5kOryPI4fIxA6HyGsc45TwHMb8VBnA4/N/7BcRSOop8brcwFdnx6vA48YGini3VwvJXDCOjHxWfeAXYIfCdF2DqJlXtxhHCw/vrhc+Pbl5aXg8Czhqj5FAWtrftikjTeesGlEM8e/jH59wNGEFgXHXQG/dZDD8P6BEniROsBwzr9bg8bkGRrMCAJHCcHnS+tGgTMKrsOLGcZFJkL64Y5EyfNPSeDsG4e9fRF6mQ1LG8XgfoFmgs5sRR5l0TY0j90ibamdXbCSI3RbdyfZ4USzcl9JqknbC1tItU/YhbNk9MprY2xQQQcYr+bVTY/EbAjSS2nwHSn4WodbQi2SZ+na5fUZxRQpGAcpb4/dca+x68MaZy1rfGuLOa8UIbNgyEn2xTDZgVYD5aRJmWgmS5kHXc1vUmntrCjS4M70ieJj/wyaS6VIKW3J82izSTBxUnqi/PDxnfHK64nU72Y2KclmK+3a8Ydseq6AlUzNc9MIdPzs1jpIyYjsmrnbDO1l/f2FMPqAocdyP1qSQsjUlsdJzJfbZoiFR77BjlqdzRjoJp2RJykhDXahxW9HbFbrSkvlam/98zDpJyH2urkbsMiTVSH0oqpjC79HpqtmD4REOT+zBPMup+0SVoBnZgYEbosHvjVfND3hITWmuG8XXSdptJeZTodj7AkWqEkMOKe72yFbdBc02TvHHTNXq8a7cJ9sQhltrkPCm7J2m43Xm6U5iIpNtZkOmpPBX08ZtM5yyloN6zmOXThdbwL8HPCbaqDQqLJTMq66JxBaZxc+Jt4FKOOTy7Y+Mxy4wPnqe6k3RzNONvec3az6vopmlOcRByVE01h/eWoG3E6ftI9RlkHMyB2zxFLmmYft0KSHefYSVsVqmSUaiiuzVmmS1p88NnZEuXdcIyfKM4NjhTf8aSivTBKQZ+0xzPt6B5UdaDsw0rTd4ph8N0wP0X5oM/Ntj5+6nY/wdY9gqCo29Y5xbsJPUWBigVWR3JNjfImTLwTZKsjVJtSkNmzyAiVSJ9mE5ryLH56NMIgMzaBP/GoHox1hWrXEVX9pIeSt2B81GDYjh4KlYBPMEEVKn2/Q0WGOhn0JKM9ajeJRqWJG4k5VhY6nPeWZwPGytjsuCuTVyrw3VdMDJxwbV4pDWUaWJqSWKFynZuXSlvd3PykwOElDI5V17GsrrfGJq/RYPHSVvsrpUlPdguP8gAvoRYTH+ed5xzzEEvMUNlbIRfaNFEYsJ3tsdK91LEe+IK6wsQat8y5eiX5wp6tFqreXTBUx1BZTFQFTAhFV8ANV5eFjo4LqDjedMRQOC3k0V5QdehvuJAXXJRXOMx1nnin5/pCLLDHnK9rkvuqdrgOpjrwDfV0WSvIUQZU1LvwUI/z6Oz2n91s3grlVtK6xjvqf/ejpxDrLUfoojZP9eblADU0+KxBrksiByoR6J2pa0SrAvKBPnO0OQp71zdkyV0wLL5gXBeue1ffrwhDtipRZUuxEgOB2eF6xXaNPRcIlY+Lex8T92wpwCd9D/lgqEocCycx1DGj7jNvMnvGMBrQEfqpPv+/fYMqVET5EGvB0/3FuR+A0kkfXagg0LEBHRtZEOeNIfqt9YPUJdGjE9xpXX2iQ3MdarkgfbxJYV4mzrMwJkGRgqAx3IIgc1qNOKkl6c5gO5mVehcrDIL6gdSBCJQOu7Ac+64g7L0FHUGaPdeRn/O7MvK0eF8VMIkHzMBB6qQZksdI5tSJojivsyq34QwBqVMPIV6E5DBuTAkskllQ+P51Vzv+X5NpO0mceXn5DARW9BafV2QvgSyW8mQhUnPkAakxPSVHnpIjv63zMnBsRIaq/PszOhpEiOkgRQaHIPIgBvYTvmu/XFJliFkitpfVJi/aIVkcOifXgXzAGHDzvGeh84oF14vy+9uTfbt3Xeq/o494FWkGjznY3cXGT6C5mpmaNjg8bEwyhPds24nqq5x1c7FLSLdn/XjZu5uwB/fMU+7GNj67TzesR+ecxGneuBT0Z9dG2AuP16X6m5vj1elvNtOlk6A9gBv2zc35kWzYBex3dpCxk09gwDyGS/mrgN426cfwvZ3k9YHxEZLwlyTRqQNyh/GsX98Kd0fBu+mqvzlep/zrNf/01yhSJ4FQf36ZP7zKNQkfXuW3W+WHxeXilAWWy0Z5Wt4RA7+s/IsI2F7qwIUfwkPncrDcTugbU7+oH/4Jrb/B3+93MIooA8cXKvk/4vS9zfF/bPGPZnxn47zN1Gthf7cwRVAqvRy5KHB2r05XTa4l+U+I/klRFOH9JQHWZaLr/HV+RKm/YxDBSXdQwH+mht7LTrkLe2vbWEF8ZeLlvvny7T9bMDXOlhEAAA=="}'}},custom_name={extra:[{color:"#FFA200",shadow_color:-10341322,text:"FoxHeadmaker Extraction Function"}],italic:0b,text:""},lore=[{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Length: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"16 Blocks",underlined:0b}],text:""},{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Author: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"TheFoxPlush",underlined:0b}],text:""}],profile={id:[I;-1551409397,-611758825,-1137461988,998522893],name:"TheFoxPlush",properties:[{name:"textures",value:"ewogICJ0aW1lc3RhbXAiIDogMTc3Mzk0MzMxMDU5NSwKICAicHJvZmlsZUlkIiA6ICJhMzg3NWYwYmRiODk0ZDE3YmMzM2I1MWMzYjg0NDAwZCIsCiAgInByb2ZpbGVOYW1lIiA6ICJUaGVGb3hQbHVzaCIsCiAgInNpZ25hdHVyZVJlcXVpcmVkIiA6IHRydWUsCiAgInRleHR1cmVzIiA6IHsKICAgICJTS0lOIiA6IHsKICAgICAgInVybCIgOiAiaHR0cDovL3RleHR1cmVzLm1pbmVjcmFmdC5uZXQvdGV4dHVyZS9kMWQ1Nzg3NTFhYzRkMjEzOWY4ODA3ZWE1NWM1MmNhM2ZhYTM3Y2M0NGU3NmMwOTBjMWYzOWZhNDA2NTQ2NzgxIiwKICAgICAgIm1ldGFkYXRhIiA6IHsKICAgICAgICAibW9kZWwiIDogInNsaW0iCiAgICAgIH0KICAgIH0sCiAgICAiQ0FQRSIgOiB7CiAgICAgICJ1cmwiIDogImh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMjhkZTRhODE2ODhhZDE4YjQ5ZTczNWEyNzNlMDg2YzE4ZjFlMzk2Njk1NjEyM2NjYjU3NDAzNGMwNmY1ZDMzNiIKICAgIH0KICB9Cn0="}]}]''',
    "export":'''{DF_NBT:4671,components:{"minecraft:custom_data":{PublicBukkitValues:{"hypercube:codetemplatedata":'{"author":"TheFoxPlush","name":"&b&lFunction &3» &bfoxheadmaker_export","version":1,"code":"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"}'}},"minecraft:custom_name":{extra:[{color:"#FFA200",shadow_color:-10341322,text:"FoxHeadmaker Extraction Function"}],italic:0b,text:""},"minecraft:lore":[{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Length: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"16 Blocks",underlined:0b}],text:""},{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Author: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"TheFoxPlush",underlined:0b}],text:""}],"minecraft:profile":{id:[I;-1551409397,-611758825,-1137461988,998522893],name:"TheFoxPlush",properties:[{name:"textures",signature:"qDqWbVRbv2hK3ik8wfBaIq9icU4qQstuxPfumbSjIv2votLAwmAyhV33I6GRd6gBoEBVyc6Kd3Q8226oj+dJFJ+A7LpDNbrbZbCM9v9dpqeXaInGvMeSq1177roqo0OtgqXt9K9iZ00JVyIPMyzUsN4Ky5LvamXR7YflFmMaPwfpyvBTgTWj2zm6GZ0Oh47BFfHSyKdUEjHnLdE+7vL5/g19C3e/hMkJvC8oUM/cnMuHs6QYBplXOV0bHAD62kdLLsNkTrtVcTyRcX2MfiuyWIe/PGNbul2VDlT32s0XBVWXcomyJ+5MI+X2DXE0nVsMwcDt8kJ4ovbK8qjlCPPSXBSpSZppyMGRLvSOGgQVYbDWyHWkctM6i+eJA5eGeZzqpbHAouxMj4xSO9HzPn4EmDVE8TsOdX9RQNGpfxlnvdU7hlfh7W7NRjnK7YWztVPhMH4QHLIrY+DVvuXKVGrtGr36pezhr/2JSxZ6WgZYofuZ0aE1ejObQiOw8MCNLkLrCC/dZJoOkpAuhTRHqs4Q5PlPwZzK+rIBc34KPhn54f4aUI6oRJPWVr8Hyrv5XpAwboByb/Yj9A7ZH89hZ1lJNfxATJQs1NvLr5N135h1cyefM4Ojsgvu9FqCZ5Vj3VxDYaBfLhIMzckTi8g9lZK1vZzSOeXInf4FD7T9uL0ot8A=",value:"ewogICJ0aW1lc3RhbXAiIDogMTc3Mzk0MzMxMDU5NSwKICAicHJvZmlsZUlkIiA6ICJhMzg3NWYwYmRiODk0ZDE3YmMzM2I1MWMzYjg0NDAwZCIsCiAgInByb2ZpbGVOYW1lIiA6ICJUaGVGb3hQbHVzaCIsCiAgInNpZ25hdHVyZVJlcXVpcmVkIiA6IHRydWUsCiAgInRleHR1cmVzIiA6IHsKICAgICJTS0lOIiA6IHsKICAgICAgInVybCIgOiAiaHR0cDovL3RleHR1cmVzLm1pbmVjcmFmdC5uZXQvdGV4dHVyZS9kMWQ1Nzg3NTFhYzRkMjEzOWY4ODA3ZWE1NWM1MmNhM2ZhYTM3Y2M0NGU3NmMwOTBjMWYzOWZhNDA2NTQ2NzgxIiwKICAgICAgIm1ldGFkYXRhIiA6IHsKICAgICAgICAibW9kZWwiIDogInNsaW0iCiAgICAgIH0KICAgIH0sCiAgICAiQ0FQRSIgOiB7CiAgICAgICJ1cmwiIDogImh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMjhkZTRhODE2ODhhZDE4YjQ5ZTczNWEyNzNlMDg2YzE4ZjFlMzk2Njk1NjEyM2NjYjU3NDAzNGMwNmY1ZDMzNiIKICAgIH0KICB9Cn0="}]}},count:1,id:"minecraft:player_head"}''',
    "terracotta":'''function foxheadmaker_extraction(headchar_item: item, ...vars: str): txt{
    line vars: dict[txt] = dict.create(vars, headchar_item.getLore());
    line headchar_deposity: txt = s"";
    for (line var, line char of vars) {
        global "%var(var)": txt = char;
        headchar_deposity.setToStyledText(headchar_deposity, char);
    }
    return headchar_deposity;
}'''
}

def popup_window(name,icon):
    window = Toplevel()
    window.title(name)
    window.iconphoto(False,icon)
    apply_theme_to_titlebar(window)
    return(window)

root = Tk()
root.title("FoxHeadmaker v2.0")
root.iconbitmap(asset(os.path.join("assets","logo.ico")))

assets = {}
for path, _, images in os.walk(asset("assets")):
    for image in images:
        if image.endswith(".png"):
            asset_path = os.path.join(path,image)
            photo_image = PhotoImage(file=asset_path)
            if "in_text" in asset_path:
                photo_image = photo_image.zoom(3,3)
            if "items" in asset_path:
                photo_image = photo_image.zoom(2,2)
            assets[str(Path(os.path.dirname(asset_path)).name)+"/"+str(Path(asset_path).name)] = photo_image

def hyperlink(url):
    webbrowser.open_new(url)

def apply_theme_to_titlebar(root): #from https://github.com/rdbende/Sun-Valley-ttk-theme
    if sys.platform == "win32":
        version = sys.getwindowsversion()

        if version.major == 10 and version.build >= 22000:
            # Set the title bar color to the background color on Windows 11 for better appearance
            pywinstyles_change_header_color(root, "#1c1c1c" if get_theme() == "dark" else "#fafafa")
        elif version.major == 10:
            pywinstyles_apply_style(root, "dark" if get_theme() == "dark" else "normal")

            # A hacky way to update the title bar's color on Windows 10 (it doesn't update instantly like on Windows 11)
            root.wm_attributes("-alpha", 0.99)
            root.wm_attributes("-alpha", 1)

def change_theme():
    if config.args["dark"]:
        # Set light theme
        set_theme("light")
    else:
        # Set dark theme
        set_theme("dark")
    config.set("dark",light_dark.get())
    apply_theme_to_titlebar(root)

def fuse_images(images):
    '''
    Pastes images in order and adjusts total canvas to contain all. Format for images is {offset:image}.
    '''
    total_width = 0
    total_height = 0
    for offset,image in images.items():
        total_width = max(total_width,offset[0]+image.size[0])
        total_height = max(total_height,offset[1]+image.size[1])
    new_image = Image.new("RGBA",(total_width,total_height),(0,0,0,0))
    for offset,image in images.items():
        new_image.paste(image,offset)
    return(new_image)

print(assets.keys())

class Notification:
    _notifications = []

    COLORS = {
        "success": {
            "accent": "#2ecc71",
            "icon": assets["in_text/success.png"],
            "sound":asset(os.path.join("assets","sounds","success.wav"))
        },
        "error": {
            "accent": "#e74c3c",
            "icon": assets["in_text/error.png"],
            "sound":asset(os.path.join("assets","sounds","error.wav"))
        },
        "warning": {
            "accent": "#f1c40f",
            "icon": assets["in_text/warning.png"],
            "sound":asset(os.path.join("assets","sounds","warning.wav"))
        },
        "info": {
            "accent": "#3498db",
            "icon": assets["in_text/info.png"],
            "sound":asset(os.path.join("assets","sounds","info.wav"))
        },
    }

    def __init__(
        self,
        parent,
        message,
        notification_type="success",
        duration=4000
    ):
        self.parent = parent
        self.message = message
        self.notification_type = notification_type
        self.duration = duration

        self.window = None
        self.target_x = 0
        self.target_y = 0
        self.current_y = 0

        self.width = 0
        self.height = 0

        self.animating_out = False

        self.show()

    # =========================================================
    # Show
    # =========================================================

    def show(self):
        colors = self.COLORS.get(
            self.notification_type,
            self.COLORS["info"]
        )

        playsound(colors["sound"],block=False)

        self.window = Toplevel(self.parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        try:
            self.window.attributes("-alpha", 0.0)
        except TclError:
            pass

        # -----------------------------------------------------
        # Outer border
        # -----------------------------------------------------

        outer = tk_Frame(
            self.window,
            bg="#151515",
            padx=1,
            pady=1
        )
        outer.pack(fill="both", expand=True)

        # -----------------------------------------------------
        # Main notification
        # -----------------------------------------------------

        main = tk_Frame(
            outer,
            bg="#202020",
            padx=14,
            pady=12
        )
        main.pack(fill="both", expand=True)

        # -----------------------------------------------------
        # Icon
        # -----------------------------------------------------

        icon = tk_Label(
            main,
            bg="#202020",
            image=colors["icon"]
        )

        icon.pack(
            side="left",
            padx=(0, 10)
        )

        # -----------------------------------------------------
        # Message
        # -----------------------------------------------------

        label = tk_Label(
            main,
            text=self.message,
            bg="#202020",
            fg="#ffffff",
            font=("Segoe UI", 10),
            justify="left",
            anchor="w",
            wraplength=300
        )

        label.pack(
            side="left",
            fill="both",
            expand=True
        )
        # -----------------------------------------------------
        # Get dimensions
        # -----------------------------------------------------

        self.window.update_idletasks()

        self.width = self.window.winfo_width()
        self.height = self.window.winfo_height()

        # -----------------------------------------------------
        # Calculate initial position
        # -----------------------------------------------------

        self._calculate_position()

        # Start slightly below the final position
        self.current_y = self.target_y + 30

        self.window.geometry(
            f"{self.width}x{self.height}"
            f"+{self.target_x}+{int(self.current_y)}"
        )

        # Add to notification list AFTER calculating base
        # position.
        self._notifications.append(self)

        # -----------------------------------------------------
        # Animate in
        # -----------------------------------------------------

        self._reposition_all()
        self._animate_in()

        # -----------------------------------------------------
        # Automatic timeout
        # -----------------------------------------------------

        self.window.after(
            self.duration,
            self.hide
        )

    # =========================================================
    # Calculate bottom-right base position
    # =========================================================

    def _calculate_position(self):
        self.parent.update_idletasks()

        root_x = self.parent.winfo_rootx()
        root_y = self.parent.winfo_rooty()

        root_width = self.parent.winfo_width()
        root_height = self.parent.winfo_height()

        margin = 20

        self.target_x = (
            root_x
            + root_width
            - self.width
            - margin
        )

        self.target_y = (
            root_y
            + root_height
            - self.height
            - margin
        )

    # =========================================================
    # Animate in
    # =========================================================

    def _animate_in(self):
        if self.window is None:
            return

        distance = self.target_y - self.current_y

        if abs(distance) <= 1:
            self.current_y = self.target_y

            self.window.geometry(
                f"{self.width}x{self.height}"
                f"+{self.target_x}+{int(self.target_y)}"
            )

            try:
                self.window.attributes(
                    "-alpha",
                    1.0
                )
            except TclError:
                pass

            return

        self.current_y += distance * 0.25

        self.window.geometry(
            f"{self.width}x{self.height}"
            f"+{self.target_x}+{int(self.current_y)}"
        )

        try:
            progress = 1 - (
                abs(distance) / 30
            )

            alpha = min(
                1.0,
                max(0.0, progress)
            )

            self.window.attributes(
                "-alpha",
                alpha
            )

        except TclError:
            pass

        self.window.after(
            10,
            self._animate_in
        )

    # =========================================================
    # Hide
    # =========================================================

    def hide(self):
        if (
            self.window is None
            or self.animating_out
        ):
            return

        self.animating_out = True

        self._animate_out()

    # =========================================================
    # Animate out
    # =========================================================

    def _animate_out(self):
        if self.window is None:
            return

        self.current_y += 8

        alpha = max(
            0,
            1 - (
                (self.current_y - self.target_y)
                / 30
            )
        )

        try:
            self.window.attributes(
                "-alpha",
                alpha
            )
        except TclError:
            pass

        self.window.geometry(
            f"{self.width}x{self.height}"
            f"+{self.target_x}+{int(self.current_y)}"
        )

        if alpha <= 0:
            self.destroy()
            return

        self.window.after(
            10,
            self._animate_out
        )

    # =========================================================
    # Destroy
    # =========================================================

    def destroy(self):
        if self.window is None:
            return

        if self in self._notifications:
            self._notifications.remove(self)

        self.window.destroy()
        self.window = None

        # Move remaining notifications
        self._reposition_all()

    # =========================================================
    # Reposition all remaining notifications
    # =========================================================

    @classmethod
    def _reposition_all(cls):
        if not cls._notifications:
            return

        offset = 0

        # Reverse means newest notification is at the bottom
        for notification in reversed(cls._notifications):

            if notification.window is None:
                continue

            notification._calculate_position()

            notification.target_y -= offset

            offset += (
                notification.height
                + 10
            )

            notification._animate_to_position()

    # =========================================================
    # Animate notification to new stack position
    # =========================================================

    def _animate_to_position(self):
        if (
            self.window is None
            or self.animating_out
        ):
            return

        distance = (
            self.target_y
            - self.current_y
        )

        if abs(distance) <= 1:
            self.current_y = self.target_y

            self.window.geometry(
                f"{self.width}x{self.height}"
                f"+{self.target_x}+{int(self.target_y)}"
            )

            return

        self.current_y += distance * 0.25

        self.window.geometry(
            f"{self.width}x{self.height}"
            f"+{self.target_x}+{int(self.current_y)}"
        )

        self.window.after(
            10,
            self._animate_to_position
        )

    @classmethod
    def bind_to_parent(cls, parent):
        cls._parent = parent

        parent.bind(
            "<Configure>",
            cls._on_parent_configure,
            add="+"
        )


    @classmethod
    def _on_parent_configure(cls, event):
        if event.widget != cls._parent:
            return

        if not cls._notifications:
            return

        cls._reposition_all()

Notification.bind_to_parent(root)

class ScrollableImage(Frame): #thanks to https://stackoverflow.com/a/56046307
    def __init__(self, master=None, **kw):
        self.image = kw.pop('image', None)
        super(ScrollableImage, self).__init__(master=master, **kw)
        self.cnvs = Canvas(self, highlightthickness=0, **kw)
        self.cnvs.create_image(0, 0, anchor='nw', image=self.image)
        # Vertical and Horizontal scrollbars
        self.v_scroll = Scrollbar(self, orient='vertical')
        self.h_scroll = Scrollbar(self, orient='horizontal')
        # Grid and configure weight.
        self.cnvs.grid(row=0, column=0,  sticky='nsew')
        self.h_scroll.grid(row=1, column=0, sticky='ew')
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # Set the scrollbars to the canvas
        self.cnvs.config(xscrollcommand=self.h_scroll.set, 
                           yscrollcommand=self.v_scroll.set)
        # Set canvas view to the scrollbars
        self.v_scroll.config(command=self.cnvs.yview)
        self.h_scroll.config(command=self.cnvs.xview)
        # Assign the region to be scrolled 
        self.cnvs.config(scrollregion=self.cnvs.bbox('all'))
        self.cnvs.bind_class(self.cnvs, "<MouseWheel>", self.mouse_scroll)

    def update_image(self, image):
        self.cnvs.delete("all")
        self.image = image
        self.cnvs.create_image(0, 0, anchor='nw', image=self.image)
        # Set canvas view to the scrollbars
        self.v_scroll.config(command=self.cnvs.yview)
        self.h_scroll.config(command=self.cnvs.xview)
        # Assign the region to be scrolled 
        self.cnvs.config(scrollregion=self.cnvs.bbox('all'))


    def mouse_scroll(self, evt):
        if evt.state == 0 :
            self.cnvs.yview_scroll(-1*(evt.delta), 'units') # For MacOS
            self.cnvs.yview_scroll(int(-1*(evt.delta/120)), 'units') # For windows
        if evt.state == 1:
            self.cnvs.xview_scroll(-1*(evt.delta), 'units') # For MacOS
            self.cnvs.xview_scroll(int(-1*(evt.delta/120)), 'units') # For windows

class Config():
    def __init__(self):
        self.path = CONFIG_PATH
        self.args = { #default arguments; overridden by existing file
            "auth_key":"",
            "last_file_dialog":HOME_DIR,
            "last_tcil_file":HOME_DIR,
            "dark": True if darkdetect_theme() == "dark" else False,
            "export_item_preference":"none",
            "remove_extension":False,
            "show_purple_tint":False,
            "inverse_scroll_items":False,
            "spritesheet_notification":True
        }
        with open(self.path,"r") as configfile:
            set_config_args = json_load(configfile)
        for key,value in set_config_args.items():
            if key in self.args.keys():
                self.args[key] = value
        with open(self.path,"w") as configfile:
            json_dump(self.args,configfile,indent=3)
    def set(self,key,value):
        self.args[key] = value
        with open(self.path,"w") as configfile:
            json_dump(self.args,configfile,indent=3)

class CustomProgressbar(Label):
    def __init__(self, master=None, max=100, **kw):
        self.variable = kw.pop("variable")
        super(CustomProgressbar, self).__init__(master=master, **kw)
        self.max = max
        self.update()
    def update(self):
        print(f"Updating progressbar: {self.variable.get()}/{self.max}")
        image = Image.open(asset(os.path.join("assets","progress_bar","empty.png"))).convert("RGBA")
        image_top = Image.open(asset(os.path.join("assets","progress_bar","full.png"))).convert("RGBA")
        image.paste(image_top.crop((0,0,round(self.variable.get()/self.max*image_top.size[0]),image_top.size[1])),(0,0))
        image = ImageTk.PhotoImage(image)
        image = image._PhotoImage__photo.zoom(2)
        self.configure(image=image)
        self.image = image

class ScrollableFrame(Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.canvas = Canvas(
            self,
            highlightthickness=0,
            bd=0,
        )

        self.hbar = Scrollbar(
            self,
            orient="horizontal",
            command=self.canvas.xview,
        )

        self.canvas.configure(
            xscrollcommand=self.hbar.set,
        )

        self.canvas.pack(
            side="top",
            fill="both",
            expand=True,
        )

        self.hbar.pack(
            side="bottom",
            fill="x",
        )

        self.content = Frame(self.canvas)

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw",
        )

        self.content.bind(
            "<Configure>",
            self._on_content_configure,
        )

        self.canvas.bind(
            "<Configure>",
            self._on_canvas_configure,
        )

        # Mouse / touchpad bindings
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _on_content_configure(self, event=None):
        bbox = self.canvas.bbox("all")

        if bbox:
            self.canvas.configure(
                scrollregion=bbox,
                height=self.content.winfo_reqheight(),
            )

    def _on_canvas_configure(self, event=None):
        bbox = self.canvas.bbox("all")

        if bbox:
            self.canvas.configure(
                scrollregion=bbox,
            )

    # ------------------------------------------------------------------
    # Mouse / touchpad scrolling
    # ------------------------------------------------------------------

    def _bind_mousewheel(self, event=None):
        self.canvas.bind_all(
            "<MouseWheel>",
            self._on_mousewheel,
            add="+",
        )

        # Linux
        self.canvas.bind_all(
            "<Button-4>",
            self._on_linux_scroll,
            add="+",
        )

        self.canvas.bind_all(
            "<Button-5>",
            self._on_linux_scroll,
            add="+",
        )

    def _unbind_mousewheel(self, event=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        self.canvas.xview_scroll(
            self._wheel_units(event.delta if inverse_scroll_items.get() else event.delta*-1),
            "units",
        )

    def _on_linux_scroll(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")

    @staticmethod
    def _wheel_units(delta):
        # Windows generally reports multiples of 120.
        # macOS / some touchpads can report smaller values.
        if abs(delta) >= 120:
            return -int(delta / 120) * 3

        return -1 if delta > 0 else 1

class ExportableItem(Button):
    def __init__(self,master,name,item_formats,icon=assets["items/apple.png"],terracotta_mode="append"):
        super(ExportableItem,self).__init__(master=master,image=icon,text=name,compound="left",style="Accent.TButton",command=self.export_item)
        self.name = name
        self.item_formats = item_formats
        self.icon = icon
        self.window_loaded = False
        self.terracotta_mode = terracotta_mode
    def export_item(self):
        if config.args["export_item_preference"]!="none":
            match config.args["export_item_preference"]:
                case "give":
                    self.export_give()
                case "codeclient":
                    self.export_codeclient()
                case "millomod":
                    self.export_millomod()
                case "terracotta":
                    self.export_terracotta()
            return
        self.window = popup_window(f"Exporting item '{self.name}'",self.icon)
        self.window_loaded = True
        frame = Frame(self.window, style='Card.TFrame', padding=(5, 6, 7, 8))
        Button(frame,compound="left",image=assets["in_text/give.png"],text="Copy /give command",command=self.export_give,cursor="hand2").pack(padx=10,pady=10,side="left")
        Button(frame,compound="left",image=assets["in_text/codeclient.png"],text="Export to CodeClient",command=self.export_codeclient,cursor="hand2").pack(padx=10,pady=10,side="left")
        Button(frame,compound="left",image=assets["in_text/millomod.png"],text="Export to Millomod",command=self.export_millomod,cursor="hand2").pack(padx=10,pady=10,side="left")
        terracotta_handle = "Append to .tcil File"
        if self.terracotta_mode == "copy":
            terracotta_handle = "Copy Terracotta Function to Clipboard"
        Button(frame,compound="left",image=assets["in_text/terracotta.png"],text=terracotta_handle,command=self.export_terracotta,cursor="hand2").pack(padx=10,pady=10,side="left")
        frame.pack(padx=10,pady=10,expand=True)
        self.remember_choice = BooleanVar(value=False)
        Checkbutton(self.window,text="Select this choice automatically next time",variable=self.remember_choice).pack(padx=10,pady=10)

    def window_destroy(self,preference="none"):
        global reset_preference_button
        if self.window_loaded:
            self.window.destroy()
            self.window_loaded = False
            if preference!="none" and config.args["export_item_preference"] == "none" and self.remember_choice.get():
                reset_preference_button.configure(state="normal")
                config.set("export_item_preference",preference)
    def export_give(self):
        pyperclip_copy(f"/give @p {self.item_formats["give"]} 1")
        self.window_destroy("give")
        Notification(root,"Copied give command to clipboard!","success")

    def export_millomod(self):
        self.window_destroy("millomod")
        Notification(root,"Sending to MilloMod...","info")
        try:
            with connect("ws://localhost:31321") as websocket:
                websocket.send(json_dumps({"type":"item","source":"FoxHeadmaker","data":f"{self.item_formats["export"]}"}))
            Notification(root,"Item sent to MilloMod","success")
        except Exception as e:
            Notification(root,"Failed to send item to MilloMod.","error")

    def export_codeclient(self):
        self.window_destroy("codeclient")
        Notification(root,"Sending to CodeClient...","info")
        try:
            with connect("ws://localhost:31375") as websocket:
                websocket.send(f"give {self.item_formats["export"]}")
            Notification(root,"Item sent to CodeClient","success")
        except Exception as e:
            Notification(root,"Failed to send item to CodeClient.","error")

    def export_terracotta(self):
        global config
        if self.terracotta_mode == "append":
            terracotta_file = filedialog.askopenfilename(
                title="Select .tcil file to append to",
                initialdir=config.args["last_tcil_file"],
                filetypes=[("Terracotta Files", "*.tcil")]
            )
            if terracotta_file == "":
                return
            self.window_destroy("terracotta")
            try:
                with open(terracotta_file,"r") as tcfile:
                    current_tcil = json_load(tcfile)
                current_tcil["items"][self.name] = self.item_formats["terracotta"]
                with open(terracotta_file,"w") as tcfile:
                    json_dump(current_tcil,tcfile,indent=3)
                Notification(root,"Added content to .tcil file!","success")
            except Exception as e:
                Notification(root,"Couldn't write to .tcil file.","error")
            config.set("last_tcil_file",terracotta_file.removesuffix(terracotta_file.split("/")[-1]))
        elif self.terracotta_mode == "copy":
            pyperclip_copy(self.item_formats["terracotta"])
            self.window_destroy("terracotta")
            Notification(root,"Copied terracotta function to clipboard!","success")      

global config
config = Config()

global worker_thread
worker_thread = None

auth_key = StringVar(value=config.args["auth_key"])

if config.args["dark"]:
    set_theme("dark")
else:
    set_theme("light")
apply_theme_to_titlebar(root)

notebook = Notebook(root)
page_spritesheets_to_chars = Frame(notebook)
page_options = Frame(notebook)

#Spritesheets to Chars
spritesheet_to_chars_images = {} #key: spritesheet name, value: list of sublists of heads sorted through chains

def clear_items():
    global frame_items_scroll_items
    for widget in frame_items_scroll_items:
        widget.destroy()
        frame_items_scroll_items = []
    frame_items_scroll_clear_button.configure(state="disabled")

def make_preview(heads_previewed,spritesheet_name):
    #measure name length
    test_image = Image.new("RGBA",(1,1),"#000000")
    test_image_draw = ImageDraw.Draw(test_image)
    test_image_draw.fontmode = "1"
    bbox = test_image_draw.textbbox((0,0),spritesheet_name,font=MINECRAFT_FONT)
    name_width = bbox[2]-bbox[0]
    name_height = bbox[3]-bbox[1]
    name_y_offset = bbox[1]

    max_head_x = len(max(heads_previewed,key=len)) #finding the biggest sublist to find how large the lore needs to get. >1 only for chain mode
    max_head_y = len(heads_previewed) #total amount of chains is how long the lore needs to get

    lore_width = max(max_head_x*8+8,name_width+9)
    lore_image = Image.new("RGBA", (lore_width,max_head_y*10+10+name_height), "#100010") #*10 because space of 2px for each line
    lore_image_draw = ImageDraw.Draw(lore_image)
    lore_image_draw.rectangle((1,1,lore_image.size[0]-2,lore_image.size[1]-2),fill="#100010",outline="#2c0863",width=1) #tooltip outline
    lore_image_draw.point([(1,1),(1,lore_image.size[1]-2),(lore_image.size[0]-2,lore_image.size[1]-2),(lore_image.size[0]-2,1)],fill="#100010") #tooltip corners
    lore_image_draw.point([(0,0),(0,lore_image.size[1]-1),(lore_image.size[0]-1,lore_image.size[1]-1),(lore_image.size[0]-1,0)],fill=(0,0,0,0)) #tooltip corners
    lore_image_draw.fontmode = "1" #no AA
    lore_image_draw.text((5,5-name_y_offset),spritesheet_name,font=MINECRAFT_FONT,fill="#623436") #shadow
    lore_image_draw.text((4,4-name_y_offset),spritesheet_name,font=MINECRAFT_FONT,fill="#d1690a")
    for y,heads in enumerate(heads_previewed):
        for x,head in enumerate(heads):
            if show_purple_tint.get():
                head = ImageChops.multiply(head,LORE_TINT)
            shadow = ImageChops.multiply(head,SHADOW_TINT)
            lore_image.paste(shadow,(x*8+5,y*10+name_height+8))
            lore_image.paste(head,(x*8+4,y*10+name_height+7))

    #lore image is complete; pasting onto apple
    item_image = fuse_images({(0,0):ITEM_APPLE_IMAGE,(10,7):lore_image})
    return(item_image)



def make_previews(): #compiles the full preview image on the right
    global spritesheet_to_chars_images
    if spritesheet_to_chars_images == {}:
        return
    global chain_mode
    item_images = {}
    previous_item_image_y = 0
    for spritesheet_name,heads_previewed in spritesheet_to_chars_images.items():
        if not(chain_mode.get()):
            heads_previewed = [ [x] for xs in heads_previewed for x in xs]
        item_image = make_preview(heads_previewed,spritesheet_name)
        item_images[(0,previous_item_image_y)] = item_image
        previous_item_image_y+= item_image.size[1]+4
    all_item_image = fuse_images(item_images)
    all_item_image_tk = ImageTk.PhotoImage(all_item_image)
    all_item_image_tk = all_item_image_tk._PhotoImage__photo.zoom(2)
    page_spritesheets_to_chars_preview.update_image(all_item_image_tk)

def seconds_to_rounded_time(seconds):
    if seconds < 60:
        return(f"{round(seconds)}s")
    if seconds < 3600:
        return(f"{floor(seconds/60)}m")
    return(f"{floor(seconds/3600)}h{floor(seconds%3600/60)}m")

def get_spritesheets():
    global spritesheet_to_chars_images
    print("opening file dialog...")
    spritesheets = filedialog.askopenfilenames(
        title="Select spritesheet(s)",
        initialdir=config.args["last_file_dialog"]
    )
    if spritesheets == "": #cancelled
        return

    get_spritesheets_spritesheet_count.set(len(spritesheets))
    head_count = 0
    transparency_warning = False
    spritesheet_to_chars_images = {} #key: spritesheet name, value: list of sublists of heads sorted through chains
    for spritesheet in spritesheets:
        spritesheet_name = spritesheet.split("/")[-1]
        if remove_extension.get():
            spritesheet_name = os.path.splitext(spritesheet_name)[0]
        current_chain = []
        spritesheet_images = []
        try:
            image_spritesheet = Image.open(spritesheet)
            image_spritesheet = image_spritesheet.convert("RGBA")
            max_x,max_y = image_spritesheet.size
            if max_x%8!=0 or max_y%8!=0: #check that the dimensions are *8
                raise(ValueError(f"Spritesheet {spritesheet}'s dimensions must be multiples of 8, not ({max_x}*{max_y})"))
            max_x//=8
            max_y//=8
            for y in range(max_y):
                for x in range(max_x):
                    tile = image_spritesheet.crop((x*8,y*8,(x+1)*8,(y+1)*8))
                    if not tile.getbbox(): #hack to detect if tile is empty
                        if len(current_chain)>0:
                            spritesheet_images.append(current_chain)
                            current_chain = []
                        continue
                    if tile.getextrema()[-1][0] < 255 and not(transparency_warning): #if tile contains transparency
                        Notification(root,"Transparency within a head cannot be handled in this format. It is recommended for tiles to not have any transparency to avoid unpredictable behavior.","error")
                        transparency_warning = True
                    head_count+=1
                    current_chain.append(tile)
                if len(current_chain)>0:
                    spritesheet_images.append(current_chain)
                    current_chain = []
        except Exception as e:
            Notification(root,f"Error opening spritesheet '{spritesheet}'. Make sure you have an image.","error")
            return
        config.set("last_file_dialog",spritesheet.removesuffix(spritesheet_name))
        spritesheet_to_chars_images[spritesheet_name] = spritesheet_images

    get_spritesheets_head_count.set(head_count)
    page_spritesheets_to_chars_prograss_bar.max = head_count
    spritesheets_to_chars_progress.set(0)
    get_spritesheets_estimated_time.set("~"+seconds_to_rounded_time(MIN_REQ_TIME*head_count))
    if get_spritesheets_spritesheet_count.get() == 1:
        Notification(root,f"Loaded 1 spritesheet.","info")
    else:
        Notification(root,f"Loaded {get_spritesheets_spritesheet_count.get()} spritesheets.","info")
    print(spritesheet_to_chars_images)
    make_previews()

def spritesheets_to_chars_compile():
    global spritesheet_to_chars_images
    global chain_mode
    global worker_thread
    if spritesheet_to_chars_images == {}:
        Notification(root,"You need to load spritesheets to compile.","error")
        return
    if auth_key.get() == "":
        Notification(root,"You need to have an API key defined in options to compile.","error")
        return
    if worker_thread:
        Notification(root,"You cannot have multiple compilations happening simultaneously.","error")
        return
    page_spritesheets_to_chars_compile_button.configure(state="disabled")
    chain_mode_button.configure(state="disabled")
    get_spritesheets_button.configure(state="disabled")
    page_spritesheets_to_chars_compile_spritesheets.pack(padx=5,pady=10,side="left")
    page_spritesheets_to_chars_compile_heads.pack(padx=5,pady=10,side="left")
    page_spritesheets_to_chars_compile_time_left.pack(padx=5,pady=10,side="left")
    page_spritesheets_to_chars_compile_spritesheets.configure(text=f"0/{get_spritesheets_spritesheet_count.get()}")
    page_spritesheets_to_chars_compile_heads.configure(text=f"0/{get_spritesheets_head_count.get()}")
    page_spritesheets_to_chars_compile_time_left.configure(text="")
    worker_thread = Thread(target=spritesheets_to_chars_process)
    worker_thread.start()

def get_head_id_from_tile(tile,name): #generates a head id from mineskin
    try:
        HEAD_TEMPLATE.paste(tile,(8,8))
        buffered = BytesIO()
        HEAD_TEMPLATE.save(buffered,format="PNG",quality=100)
        while True:
            request_time = time()
            response = requests_post(
                url='https://api.mineskin.org/generate/upload',
                data={"name":name,"visibility":0},
                files={"file":("obfuscated/path/to/file", buffered.getvalue(), 'text/x-spam')},
                headers={"User-Agent": "FoxHeadmaker","Authorization": "Bearer " + config.args["auth_key"]}
            )
            request_time = time() - request_time
            sleep_time = 0
            if response.status_code != 200: #error somewhere...
                if response.status_code==403: #unauthorized access; wrong api key often times
                    Notification(root,"Your api key is likely incorrect. Shutting down task...","error")
                    return(None)
                else:
                    Notification(root,f"Error from mineskin.org ({response.status_code}). Trying again in 5s...","error")
                    sleep(5)
                    continue
            break
        result = response.json()["data"]["texture"]["value"] #raw output value
        result = base64_compressor_value(result) #compresses the value by stripping useless stuff
        #computing remaining time
        if response.json()["rateLimit"]["limit"]["remaining"]==0:
            sleep_time = response.json()["rateLimit"]["limit"]["reset"]-time()
        else:
            sleep_time = max(MIN_REQ_TIME-request_time,0)
        if sleep_time > 0:
            sleep(sleep_time)
        return(result)

    except Exception as e:
        Notification(root,"A critical error occured grabbing the mineskin.org code.")
        logging.exception("Error in get_head_id_from_tile")

def base64_compressor_value(value):
    decoded = b64decode(value.encode("ascii")).decode("ascii")
    decoded = json_loads(decoded)
    stripped_decoded = {"textures":decoded["textures"]}
    encoded = b64encode(json_dumps(stripped_decoded).encode("ascii")).decode("ascii")
    return(encoded)

def spritesheets_to_chars_process():
    global spritesheet_to_chars_images
    global chain_mode
    global spritesheets_to_chars_progress, page_spritesheets_to_chars_prograss_bar
    global get_spritesheets_head_count
    global worker_thread
    spritesheets_to_chars_progress.set(0)
    try: #giant try block to catch any error lmao
        # make sure all heads have a code; run through mineskin or get id from cache

        with open(HEAD_ID_CACHE_PATH,"r") as head_id_cache_file:
            head_id_cache = json_load(head_id_cache_file)
        spritesheet_i = 0
        start_time = monotonic()
        for spritesheet,spritesheet_tiles in spritesheet_to_chars_images.items():
            first_tile_base64 = None
            spritesheet_i+=1
            spritesheet_head_ids = [] #all ids will end here
            for tiles in spritesheet_tiles:
                current_chain = []
                for tile in tiles:
                    buffered = BytesIO()
                    tile.save(buffered,format="PNG",quality=100)
                    tile_base64 = b64encode(buffered.getvalue()).decode("utf-8") #key of image in cache
                    if not(first_tile_base64):
                        first_tile_base64 = tile_base64
                    if tile_base64 in head_id_cache: #head id exists!
                        head_id = head_id_cache[tile_base64]
                    else:
                        head_id = get_head_id_from_tile(tile,spritesheet)
                        head_id_cache[tile_base64] = head_id
                        with open(HEAD_ID_CACHE_PATH,"w") as head_id_cache_file:
                            json_dump(head_id_cache,head_id_cache_file,indent=3)
                    print("NEW COMPILED HEAD")
                    print(head_id)
                    current_chain.append(head_id)
                    #visual stuff
                    spritesheets_to_chars_progress.set(spritesheets_to_chars_progress.get()+1)
                    page_spritesheets_to_chars_prograss_bar.update()
                    elapsed = monotonic() - start_time
                    rate = None
                    if spritesheets_to_chars_progress.get() + 1 > 0:
                        rate = (spritesheets_to_chars_progress.get()+1)/elapsed
                    remaining = (get_spritesheets_head_count.get()-spritesheets_to_chars_progress.get())/rate if rate else 0
                    page_spritesheets_to_chars_compile_time_left.configure(text=seconds_to_rounded_time(remaining))
                    page_spritesheets_to_chars_compile_heads.configure(text=f"{spritesheets_to_chars_progress.get()}/{get_spritesheets_head_count.get()}")
                spritesheet_head_ids.append(current_chain)
            # compile all values into a given item
            if not(chain_mode.get()):
                spritesheet_head_ids = [ [x] for xs in spritesheet_head_ids for x in xs]
            lore = []
            for chain in spritesheet_head_ids:
                chain_text = []
                for head_id in chain:
                    chain_text.append('{player:{properties:[{name:"textures",value:"'+head_id+'"}]}}')
                if len(chain_text) == 1:
                    lore.append(chain_text[0])
                else:
                    lore.append(f"[{",".join(chain_text)}]")
            lore = f"[{",".join(lore)}]"
            item_export_1 = 'apple[lore='+lore+',custom_name={"color":"#FFA200","bold":true,"italic":false,"shadow_color":-10341322,"text":"'+spritesheet+'"}]'
            item_export_2 = '{count:1,id:"minecraft:apple",components:{"custom_name":{"color":"#FFA200","bold":true,"italic":false,"shadow_color":-10341322,"text":"'+spritesheet+'"},"lore":'+lore+'}}'
            item_export_3 = {
                'data':'{components:{"custom_name":{color:"#FFA200",bold:true,italic:false,shadow_color:-10341322,text:"'+spritesheet+'"},"lore":'+lore+'},count:1,id:"minecraft:apple"}',
                'image':f"data:image/png;base64,{first_tile_base64}",
                'version':4440
                }
            item_exports = {"give":item_export_1,"export":item_export_2,"terracotta":item_export_3}
            page_spritesheets_to_chars_compile_spritesheets.configure(text=f"{spritesheet_i}/{get_spritesheets_spritesheet_count.get()}")
            item_widget = ExportableItem(frame_items_scroll.content,spritesheet,item_exports)
            frame_items_scroll_items.append(item_widget)
            frame_items_scroll_clear_button.configure(state="normal")
            item_widget.pack(padx=10,pady=10,side="left")
            if spritesheet_notification.get():
                Notification(root,f"Finished compiling '{spritesheet}'","success")
        page_spritesheets_to_chars_compile_spritesheets.pack_forget()
        page_spritesheets_to_chars_compile_heads.pack_forget()
        page_spritesheets_to_chars_compile_time_left.pack_forget()
        page_spritesheets_to_chars_compile_button.configure(state="normal")
        chain_mode_button.configure(state="normal")
        get_spritesheets_button.configure(state="normal")
        Notification(root,"Compilation finished!","success")
        worker_thread = None
    except Exception as e:
        Notification(root,f"Critical error in compilation process: {e}","error")
        logging.exception("Error in spritesheets_to_chars_process")

page_spritesheets_to_chars_left = Frame(page_spritesheets_to_chars)

page_spritesheets_to_chars_left_above = Frame(page_spritesheets_to_chars_left, style='Card.TFrame', padding=(5, 6, 7, 8))

get_spritesheets_frame = Frame(page_spritesheets_to_chars_left_above, style='Card.TFrame', padding=(5, 6, 7, 8))
get_spritesheets_button = Button(get_spritesheets_frame,text="Choose spritesheet(s)...",command=get_spritesheets,cursor="hand2")
get_spritesheets_button.pack(padx=10,pady=10,side="left")
get_spritesheets_spritesheet_count = IntVar(value=0)
Label(get_spritesheets_frame,image=assets["in_text/spritesheet.png"],compound="left",textvariable=get_spritesheets_spritesheet_count).pack(padx=5,pady=10,side="left")
get_spritesheets_head_count = IntVar(value=0)
Label(get_spritesheets_frame,image=assets["in_text/head.png"],compound="left",textvariable=get_spritesheets_head_count).pack(padx=5,pady=10,side="left")
get_spritesheets_estimated_time = StringVar(value="~0s")
Label(get_spritesheets_frame,image=assets["in_text/clock.png"],compound="left",textvariable=get_spritesheets_estimated_time).pack(padx=5,pady=10,side="left")
get_spritesheets_frame.pack(padx=10,pady=10,expand=True)

chain_mode_frame = Frame(page_spritesheets_to_chars_left_above, style='Card.TFrame', padding=(5, 6, 7, 8))
chain_mode = BooleanVar(value=False)
chain_mode_button = Checkbutton(chain_mode_frame,style="Switch.TCheckbutton",variable=chain_mode,cursor="hand2",command=make_previews)
chain_mode_button.pack(side="left")
Label(chain_mode_frame,image=assets["in_text/chain.png"],text="Chain Mode",compound="left").pack(side="left")
chain_mode_frame.pack(padx=10,pady=10,expand=True)

page_spritesheets_to_chars_left_below = Frame(page_spritesheets_to_chars_left, style='Card.TFrame', padding=(5, 6, 7, 8))

page_spritesheets_to_chars_left_below_compile = Frame(page_spritesheets_to_chars_left_below)
page_spritesheets_to_chars_compile_button = Button(page_spritesheets_to_chars_left_below_compile,text="Compile",style='Accent.TButton',cursor="hand2",command=spritesheets_to_chars_compile)
page_spritesheets_to_chars_compile_button.pack(padx=10,pady=10,side="left")
page_spritesheets_to_chars_compile_spritesheets = Label(page_spritesheets_to_chars_left_below_compile,image=assets["in_text/spritesheet.png"],text="",compound="left")
page_spritesheets_to_chars_compile_heads = Label(page_spritesheets_to_chars_left_below_compile,image=assets["in_text/head.png"],text="",compound="left")
page_spritesheets_to_chars_compile_time_left = Label(page_spritesheets_to_chars_left_below_compile,image=assets["in_text/clock.png"],text="",compound="left")
page_spritesheets_to_chars_left_below_compile.pack()


spritesheets_to_chars_progress = IntVar(value=0)
page_spritesheets_to_chars_prograss_bar = CustomProgressbar(page_spritesheets_to_chars_left_below,variable=spritesheets_to_chars_progress)
page_spritesheets_to_chars_prograss_bar.pack()

page_spritesheets_to_chars_right = Frame(page_spritesheets_to_chars, style='Card.TFrame', padding=(5, 6, 7, 8))
Label(page_spritesheets_to_chars_right,text="Item Preview").pack(padx=10,pady=10,expand=True)
page_spritesheets_to_chars_preview = ScrollableImage(page_spritesheets_to_chars_right,image=assets["items/barrier.png"])
page_spritesheets_to_chars_preview.pack()

page_spritesheets_to_chars_left_above.pack(padx=10,pady=10)
page_spritesheets_to_chars_left_below.pack(padx=10,pady=10)
page_spritesheets_to_chars_left.pack(padx=10,pady=10,side="left")
page_spritesheets_to_chars_right.pack(padx=10,pady=10,side="left")
#Options Page

page_options_1 = Frame(page_options)

external_links = Frame(page_options_1, style='Card.TFrame', padding=(5, 6, 7, 8))
button_github = Button(external_links,text="GitHub",cursor="hand2")
button_github.bind("<Button-1>", lambda e: hyperlink("https://github.com/TheFoxPlush/FoxHeadmaker"))
button_github.pack(padx=10,pady=10,side="left")
button_github = Button(external_links,text="Discord",cursor="hand2")
button_github.bind("<Button-1>", lambda e: hyperlink("https://discord.gg/xjpaRGCTgY"))
button_github.pack(padx=10,pady=10,side="left")
button_github = Button(external_links,text="Twitch",cursor="hand2")
button_github.bind("<Button-1>", lambda e: hyperlink("https://twitch.tv/thefoxplush"))
button_github.pack(padx=10,pady=10,side="left")
external_links.pack(padx=10,pady=10,side="left")

light_dark_mode_option = Frame(page_options_1, style='Card.TFrame', padding=(5, 6, 7, 8))
Label(light_dark_mode_option,image=assets["in_text/sun.png"]).pack(side="left")
light_dark = BooleanVar(value=config.args["dark"])
Checkbutton(light_dark_mode_option,style="Switch.TCheckbutton",variable=light_dark,command=change_theme,cursor="hand2").pack(side="left")
Label(light_dark_mode_option,image=assets["in_text/moon.png"]).pack(side="left")
light_dark_mode_option.pack(padx=10,pady=10,side="left")

ExportableItem(page_options_1,"Extraction Function",EXTRACTION_FUNCTION_ITEM_FORMATS,assets["items/ender_chest.png"],terracotta_mode="copy").pack(padx=10,pady=10,expand=True,side="left")

page_options_2 = Frame(page_options)

auth_key_frame = Frame(page_options_2, style='Card.TFrame', padding=(5, 6, 7, 8))
Label(auth_key_frame,text="MineSkin API Key").pack(padx=10,pady=10,side="left")
Entry(auth_key_frame,textvariable=auth_key,show="\u2022").pack(padx=10,pady=10,side="left")
auth_key.trace_add("write",lambda *args: config.set("auth_key",auth_key.get()))
link = Label(auth_key_frame,text="How do I get a key?",foreground="blue",cursor="hand2")
link.bind("<Button-1>", lambda e: hyperlink("https://account.mineskin.org/keys"))
link.pack(padx=10,pady=10,side="left")
auth_key_frame.pack(padx=10,pady=10,side="left")

def reset_preference():
    reset_preference_button.configure(state="disabled")
    config.set("export_item_preference","none")
reset_preference_button = Button(page_options_2,text="Reset Item Export Preference",state="disabled",command=reset_preference)
if config.args["export_item_preference"]!="none":
    reset_preference_button.configure(state="normal")
reset_preference_button.pack(padx=10,pady=10,side="left")

toggleable_options_frame = Frame(page_options, style='Card.TFrame', padding=(5, 6, 7, 8))
remove_extension = BooleanVar(value=config.args["remove_extension"])
Checkbutton(toggleable_options_frame,variable=remove_extension,text="Remove file extension for spritesheet names",command=lambda *args: config.set("remove_extension",remove_extension.get())).grid(padx=10,pady=10,row=0,column=0)
show_purple_tint = BooleanVar(value=config.args["show_purple_tint"])
Checkbutton(toggleable_options_frame,variable=show_purple_tint,text="Show natural lore purple tint on preview",command=lambda *args: config.set("show_purple_tint",show_purple_tint.get())).grid(padx=10,pady=10,row=1,column=0)
inverse_scroll_items = BooleanVar(value=config.args["inverse_scroll_items"])
Checkbutton(toggleable_options_frame,variable=inverse_scroll_items,text="Invert item scrolling direction",command=lambda *args: config.set("inverse_scroll_items",inverse_scroll_items.get())).grid(padx=10,pady=10,row=0,column=1)
spritesheet_notification = BooleanVar(value=config.args["spritesheet_notification"])
Checkbutton(toggleable_options_frame,variable=spritesheet_notification,text="Notify when individual spritesheets are complete",command=lambda *args: config.set("spritesheet_notification",spritesheet_notification.get())).grid(padx=10,pady=10,row=1,column=1)
page_options_1.pack(padx=10,pady=10)
page_options_2.pack(padx=10,pady=10)
toggleable_options_frame.pack(padx=10,pady=10)

notebook.add(page_spritesheets_to_chars, text='Spritesheets ➤ Chars')
notebook.add(page_options, text='Options')

notebook.pack(pady=10,padx=10)

frame_items = Frame(root, style='Card.TFrame', padding=(5, 6, 7, 8))
frame_items_scroll = ScrollableFrame(frame_items)
frame_items_scroll_clear_button = Button(frame_items_scroll.content,text="Clear",image=assets["items/barrier.png"],compound="left",state="disabled",command=clear_items)
frame_items_scroll_clear_button.pack(padx=10,pady=10,side="left")
frame_items_scroll_items = []
frame_items_scroll.pack(side="top",fill="both",expand=True)
frame_items.pack()

def verify_update():
    global update_window
    try:
        response = requests_get(LATEST_URL_API,timeout=5)
        latest_version = response.json()["tag_name"]
        if latest_version and version.parse(latest_version[1:]) > version.parse(__version__):
            update_window = popup_window("An update is available!",assets["items/ender_chest.png"])
            Label(update_window,text="An update is available on the GitHub!").pack(padx=10,pady=10)
            Button(update_window,text=latest_version,image=assets["in_text/codeclient.png"],compound="left",command=new_update).pack(padx=10,pady=10)
    except Exception as e:
        return

def new_update():
    global update_window
    update_window.destroy()
    hyperlink("https://github.com/TheFoxPlush/FoxHeadmaker/releases/latest")

verify_update()

root.mainloop()