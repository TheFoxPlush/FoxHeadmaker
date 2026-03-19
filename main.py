from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Header, Input, Collapsible, Link, Button, DirectoryTree, Static, LoadingIndicator, ProgressBar, Checkbox
from textual.containers import HorizontalGroup, VerticalScroll, Center
from textual.screen import ModalScreen, Screen
from PIL import Image
import os
from json import load as json_load
from json import loads as json_loads
from json import dump as json_dump
from json import dumps as json_dumps
from io import BytesIO
from rich.text import Text
from time import sleep, time
from threading import Thread as thread
from requests import post
from base64 import b64decode,b64encode
from pyperclip import copy as pyperclip_copy
from websockets.sync.client import connect

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

CACHE_DIR = os.path.join(user_cache_dir_from_platformdirs(),"FoxHeadmaker")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

CACHE_HEADS_DIR = os.path.join(CACHE_DIR,"heads")
if not os.path.exists(CACHE_HEADS_DIR):
    os.makedirs(CACHE_HEADS_DIR)

CACHE_VALUES_DIR = os.path.join(CACHE_DIR,"values")
if not os.path.exists(CACHE_VALUES_DIR):
    os.makedirs(CACHE_VALUES_DIR)

HOME_DIR = os.path.expanduser("~/Desktop")

CONFIG_PATH = os.path.join(CACHE_DIR,"config.json")

HEAD_TEMPLATE = Image.open(BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00@\x00\x00\x00@\x02\x03\x00\x00\x00\xd7\x07\x99M\x00\x00\x00\tPLTE\x00\x00\x00 \x018\xff\xfc\xfdI\xad\x01\xf5\x00\x00\x00\x01tRNS\x00@\xe6\xd8f\x00\x00\x01UIDATx\x9c\xc5R\xc1J\xc3@\x14\x9c\xdd\xec\x9e\xd2B\xa0\xf1;L\x0f\x1e\xc5\x15z\xec!`r\xf0\x1b\xfc\xb4(\xb4\x90\xa3\x87-\xe8Mi\xff\xc3\x06\x025\xa74<\xd9\xddD\xd3PE\x11\xf4A\xd8e\xf6\xedd\xde\xec0 \x05\x90\xa1+\xfe\xbe\xfbS\x80\x19\x15\xe8)\xe1\xff\xa3\x83g@f4\xa4@\x9a\xfer\x16W\xd9\x91+\t\xc4\x0c\x80\xe8\x00Q\x04\x11C0\xa5pY\xbb\x8e\t\x04\x01\xdeC\xe1+\x07\x14vi>8`\x8b\x14\xaa\x16\x98ThPI\rG\xd1\xd3!\xeb\x81\x8e\xb6\xe3\x93Y\xd2\xa1\x1f/R\x08\xe3J\xd6u\x84\xfe\xf9\xe8\xe0\xca\x16\x14\x1d\n\x03\xdbt\x1b\xcb\xa7\x1e\t{\xe7\x87\x1b[\x0f\x7f\xdb+\x8e@\x01\xac\xb5H\xd9\x0e\xa6b\x9c$\x12A\xec\xac\x93\xde\xd3kX\x17\xf5\xac\xc9\xe7\xa5\x01j\xa6D\xb1\x86d\xfaj\xebHi\xb9\x00\xe0\x93\xba5\xa4\x02h.\xc2\x15Pa\x1d\x97z\xf8P\xeaf\xa0C\x1f\x11\x06\x9b\x8a\xde\xc7\x87\xe7?\xce\xc7\xb72\xc6\x12\x99(\xc8\x18\x90\x97f\x12\xe1\xdd\xd1\x16\x92\x16q)\x9e\x83\xa9w/F\xaaD\xe8\x9f\xed\xf3\xf1n\x0co\xa58\xcb\x81B\x92\xc6\x8eEhh\xe3Hk\r\x8cI\x9b\xdcp\x8aa\xcc\xa0\xf9\xa9\xb2\xb9a\xd7\xac\rF[\xc2>\xd8W\xc2\xde\x00W\xd7h\x14\xb7\xeb\x99\x82\x00\x00\x00\x00IEND\xaeB`\x82')).convert("RGBA")

MIN_REQ_TIME = 4

FUNCTION_ITEM = '''player_head[custom_data={PublicBukkitValues:{"hypercube:codetemplatedata":'{"author":"TheFoxPlush","name":"&b&lFunction &3» &bfoxheadmaker_export","version":1,"code":"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"}'}},custom_name={extra:[{color:"#FFA200",shadow_color:-10341322,text:"FoxHeadmaker Extraction Function"}],italic:0b,text:""},lore=[{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Length: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"16 Blocks",underlined:0b}],text:""},{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Author: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"TheFoxPlush",underlined:0b}],text:""}],profile={id:[I;-1551409397,-611758825,-1137461988,998522893],name:"TheFoxPlush",properties:[{name:"textures",value:"ewogICJ0aW1lc3RhbXAiIDogMTc3Mzk0MzMxMDU5NSwKICAicHJvZmlsZUlkIiA6ICJhMzg3NWYwYmRiODk0ZDE3YmMzM2I1MWMzYjg0NDAwZCIsCiAgInByb2ZpbGVOYW1lIiA6ICJUaGVGb3hQbHVzaCIsCiAgInNpZ25hdHVyZVJlcXVpcmVkIiA6IHRydWUsCiAgInRleHR1cmVzIiA6IHsKICAgICJTS0lOIiA6IHsKICAgICAgInVybCIgOiAiaHR0cDovL3RleHR1cmVzLm1pbmVjcmFmdC5uZXQvdGV4dHVyZS9kMWQ1Nzg3NTFhYzRkMjEzOWY4ODA3ZWE1NWM1MmNhM2ZhYTM3Y2M0NGU3NmMwOTBjMWYzOWZhNDA2NTQ2NzgxIiwKICAgICAgIm1ldGFkYXRhIiA6IHsKICAgICAgICAibW9kZWwiIDogInNsaW0iCiAgICAgIH0KICAgIH0sCiAgICAiQ0FQRSIgOiB7CiAgICAgICJ1cmwiIDogImh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMjhkZTRhODE2ODhhZDE4YjQ5ZTczNWEyNzNlMDg2YzE4ZjFlMzk2Njk1NjEyM2NjYjU3NDAzNGMwNmY1ZDMzNiIKICAgIH0KICB9Cn0="}]}]'''
FUNCTION_ITEM_EXPORTS = '''{DF_NBT:4671,components:{"minecraft:custom_data":{PublicBukkitValues:{"hypercube:codetemplatedata":'{"author":"TheFoxPlush","name":"&b&lFunction &3» &bfoxheadmaker_export","version":1,"code":"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"}'}},"minecraft:custom_name":{extra:[{color:"#FFA200",shadow_color:-10341322,text:"FoxHeadmaker Extraction Function"}],italic:0b,text:""},"minecraft:lore":[{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Length: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"16 Blocks",underlined:0b}],text:""},{extra:[{bold:0b,color:"gray",italic:0b,obfuscated:0b,strikethrough:0b,text:"Author: ",underlined:0b},{bold:0b,color:"#D4D4D4",italic:0b,obfuscated:0b,strikethrough:0b,text:"TheFoxPlush",underlined:0b}],text:""}],"minecraft:profile":{id:[I;-1551409397,-611758825,-1137461988,998522893],name:"TheFoxPlush",properties:[{name:"textures",signature:"qDqWbVRbv2hK3ik8wfBaIq9icU4qQstuxPfumbSjIv2votLAwmAyhV33I6GRd6gBoEBVyc6Kd3Q8226oj+dJFJ+A7LpDNbrbZbCM9v9dpqeXaInGvMeSq1177roqo0OtgqXt9K9iZ00JVyIPMyzUsN4Ky5LvamXR7YflFmMaPwfpyvBTgTWj2zm6GZ0Oh47BFfHSyKdUEjHnLdE+7vL5/g19C3e/hMkJvC8oUM/cnMuHs6QYBplXOV0bHAD62kdLLsNkTrtVcTyRcX2MfiuyWIe/PGNbul2VDlT32s0XBVWXcomyJ+5MI+X2DXE0nVsMwcDt8kJ4ovbK8qjlCPPSXBSpSZppyMGRLvSOGgQVYbDWyHWkctM6i+eJA5eGeZzqpbHAouxMj4xSO9HzPn4EmDVE8TsOdX9RQNGpfxlnvdU7hlfh7W7NRjnK7YWztVPhMH4QHLIrY+DVvuXKVGrtGr36pezhr/2JSxZ6WgZYofuZ0aE1ejObQiOw8MCNLkLrCC/dZJoOkpAuhTRHqs4Q5PlPwZzK+rIBc34KPhn54f4aUI6oRJPWVr8Hyrv5XpAwboByb/Yj9A7ZH89hZ1lJNfxATJQs1NvLr5N135h1cyefM4Ojsgvu9FqCZ5Vj3VxDYaBfLhIMzckTi8g9lZK1vZzSOeXInf4FD7T9uL0ot8A=",value:"ewogICJ0aW1lc3RhbXAiIDogMTc3Mzk0MzMxMDU5NSwKICAicHJvZmlsZUlkIiA6ICJhMzg3NWYwYmRiODk0ZDE3YmMzM2I1MWMzYjg0NDAwZCIsCiAgInByb2ZpbGVOYW1lIiA6ICJUaGVGb3hQbHVzaCIsCiAgInNpZ25hdHVyZVJlcXVpcmVkIiA6IHRydWUsCiAgInRleHR1cmVzIiA6IHsKICAgICJTS0lOIiA6IHsKICAgICAgInVybCIgOiAiaHR0cDovL3RleHR1cmVzLm1pbmVjcmFmdC5uZXQvdGV4dHVyZS9kMWQ1Nzg3NTFhYzRkMjEzOWY4ODA3ZWE1NWM1MmNhM2ZhYTM3Y2M0NGU3NmMwOTBjMWYzOWZhNDA2NTQ2NzgxIiwKICAgICAgIm1ldGFkYXRhIiA6IHsKICAgICAgICAibW9kZWwiIDogInNsaW0iCiAgICAgIH0KICAgIH0sCiAgICAiQ0FQRSIgOiB7CiAgICAgICJ1cmwiIDogImh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMjhkZTRhODE2ODhhZDE4YjQ5ZTczNWEyNzNlMDg2YzE4ZjFlMzk2Njk1NjEyM2NjYjU3NDAzNGMwNmY1ZDMzNiIKICAgIH0KICB9Cn0="}]}},count:1,id:"minecraft:player_head"}'''

class Config():
    def __init__(self) -> None:
        #default values
        self.auth_key = ""
        self.user_agent = "FoxHeadmaker"
        self.last_file_dialog = HOME_DIR
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH,"r") as configfile:
                config_dict = json_load(configfile)
            for key,value in config_dict.items():
                setattr(self,key,value)
    def save(self) -> None:
        with open(CONFIG_PATH,"w") as configfile:
            json_dump(self.__dict__,configfile,indent=3)

class FilePicker(ModalScreen[str]):
    """Modal screen that returns a selected file path."""
    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Input(placeholder="Enter a path",value=config.last_file_dialog),
            DirectoryTree(config.last_file_dialog,id="directory_tree"),
        )
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.dismiss(str(event.path))
        config.last_file_dialog = str(event.path.parent)
        config.save()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if not(os.path.isdir(event.value)):
            app.notify("Not a valid folder.",severity="error")
            return
        self.query_one("#directory_tree",DirectoryTree).path = event.value
        self.query_one("#directory_tree",DirectoryTree).reload()

def image_to_static_text(image: Image.Image) -> str:
    image = image.convert("RGB")
    width, height = image.size
    pixels = image.load()

    lines = []

    for y in range(height):
        row = ""
        for x in range(width):
            r, g, b = pixels[x, y]
            row += f"[on rgb({r},{g},{b})]  [/]"
        lines.append(row)

    return "\n".join(lines)

def save_values(values,name):
    with open(f"{CACHE_VALUES_DIR}/{name}.json","w") as valuesfile:
        json_dump(values,valuesfile,indent=3)

def skinify_multiple(current_head_files):
    values = {}
    save_values(values,app.current_spritesheet_name)
    process_ran = True
    for head_file in current_head_files:
        with Image.open(CACHE_HEADS_DIR+"/"+head_file,"r") as skin_image:
            head_image = skin_image.crop((8,8,16,16))
            app.query_one("#loadingbar_headtexture",Static).update(f"[underline]🎨 Head texture[/]\n{image_to_static_text(head_image)}")
        app.query_one("#loadingbar_mineskin",Static).update(f"[underline]💻 mineskin.org[/]\n[italic gray]Waiting for response...[/]")
        app.query_one("#loadingbar_skinvalue",Static).update(f"[underline]💾 Skin Value[/]\n[italic gray]Waiting for response...[/]")
        value = skinify(f"{CACHE_HEADS_DIR}/{head_file}",f"{app.current_spritesheet_name}_{head_file}")
        if not(value): #task has been shut down
            process_ran = False
            break
        else:
            values[f"{app.current_spritesheet_name}_{head_file}"] = value
            save_values(values,app.current_spritesheet_name)
            app.query_one('#progressbar',ProgressBar).advance(1)
    if process_ran:
        make_item(app.current_spritesheet_name)
    else:
        app.query_one("#loadingbar_headtexture",Static).update(f"[underline]🎨 Head texture[/]\n")
        app.query_one("#loadingbar_mineskin",Static).update(f"[underline]💻 mineskin.org[/]\n")
        app.query_one("#loadingbar_skinvalue",Static).update(f"[underline]💾 Skin Value[/]\n")


def make_item(name):
    chain_mode = app.query_one("#chain_mode",CustomCheck).value
    if chain_mode:
        current_chain = []
    try:
        with open(f"{CACHE_VALUES_DIR}/{name}.json","r") as valuesfile:
            values = json_load(valuesfile)
        lore = []
        for key,value in values.items():
            line = '{player:{properties:[{name:"textures",value:"'+value+'"}]}}'
            if chain_mode:
                chain_progress = os.path.splitext(key.split("@")[-1])[0]
                if chain_progress == "0" and len(current_chain) > 0:
                    current_chain = "["+",".join(current_chain)+"]"
                    lore.append(current_chain)
                    current_chain = []
                current_chain.append(line)
            else:
                lore.append(line)
        if chain_mode and len(current_chain)>0:
            lore.append(current_chain)
        lore = "["+",".join(lore)+"]"
        app.item = 'apple[lore='+lore+',custom_name={"color":"#FFA200","italic":false,"shadow_color":-10341322,"text":"'+name+'"}]'
        app.item_exports = '{count:1,id:"minecraft:apple",components:{"custom_name":{"color":"#FFA200","italic":false,"shadow_color":-10341322,"text":"'+name+'"},"lore":'+lore+'}}'
        app.query_one('#item_indicator',Static).update(f"🍎 Item '{name}' is ready!")
    except Exception as e:
        app.notify(f"{e}",title="Error in item compilation: Contact TheFoxPlush",severity="error")

def send_clipboard(item):
    pyperclip_copy(f"/give @p {item} 1")
    app.notify("Give command copied to clipboard",title="Success!")

def send_millomod(item): #must be in format item_exports
    try:
        with connect("ws://localhost:31321") as websocket:
            websocket.send(json_dumps({"type":"item","source":"FoxHeadmaker","data":f"{item}"}))
        app.notify("Item sent to MilloMod",title="Success!")
    except Exception as e:
        app.notify(f"{e}",title="Error sending to MilloMod",severity="error")

def send_codeclient(item): #must be in format item_exports
    try:
        with connect("ws://localhost:31375") as websocket:
            websocket.send(f"give {item}")
        app.notify("Item sent to CodeClient",title="Success!")
    except Exception as e:
        app.notify(f"{e}",title="Error sending to CodeClient",severity="error")

def skinify(headfile,name):
    with open(headfile, 'rb') as file:
        request_time = time()
        response = post(
            url='https://api.mineskin.org/generate/upload',
            data={"name":name,"visibility":0},
            files={"file":(headfile, file, 'text/x-spam')},
            headers={"User-Agent": config.user_agent,"Authorization": "Bearer " + config.auth_key}
        )
        request_time = time() - request_time
        sleep_time = 0
        if response.status_code!=200:
            if response.status_code==403: #unauthorized access. Likely smth wrong with api key
                app.notify("Your api key is likely incorrect. Shutting down task...",title=f"Error from mineskin.org. Unauthorized access",severity="error")
                return(None)
            else:
                app.notify("Trying again in 5s...",title=f"Error from mineskin.org. Response status code: {response.status_code}.",severity="error")
                sleep(5)
                result = skinify(headfile,name)
        else:
            result = response.json()['data']['texture']['value']
            if response.json()["rateLimit"]["limit"]["remaining"]==0:
                sleep_time = response.json()["rateLimit"]["limit"]["reset"]-time()
            else:
                sleep_time = max(MIN_REQ_TIME-request_time,0)
            formatted_response = f"Response info\nRequest time: {round(request_time*10)/10}s\nStatus code: {response.status_code}\nRequests remaining this minute: {response.json()["rateLimit"]["limit"]["remaining"]}\nLimit reset in {round((response.json()["rateLimit"]["limit"]["reset"]-time())*10)/10}s\nSleeping for {round(sleep_time*10)/10}s"
            app.query_one("#loadingbar_mineskin",Static).update(f"[underline]💻 mineskin.org[/]\n[italic gray]{formatted_response}[/]")
        result = base64_compressor_value(result)
        app.query_one("#loadingbar_skinvalue",Static).update(f"[underline]💾 Skin Value[/]\n[italic gray]{result}[/]")
        if sleep_time > 0:
            sleep(sleep_time)
        return(result)

def base64_compressor_value(value):
    decoded = b64decode(value.encode("ascii")).decode("ascii")
    decoded = json_loads(decoded)
    stripped_decoded = {"textures":decoded["textures"]}
    encoded = b64encode(json_dumps(stripped_decoded).encode("ascii")).decode("ascii")
    return(encoded)

def clear_cache():
    total_size = 0
    total_files = 0
    for head_file in os.listdir(CACHE_HEADS_DIR):
        total_files+=1
        total_size+=os.path.getsize(os.path.join(CACHE_HEADS_DIR,head_file))
        os.remove(os.path.join(CACHE_HEADS_DIR,head_file))
    
    app.notify(f"Cleared {total_files} head files, saving {total_size/(1<<17):,.0f} Mb", title="Cache Cleared")
    app.reset_head_compilation()

#from: https://blog.pythonlibrary.org/2026/03/16/textual-creating-a-custom-checkbox/
class CustomCheck(Checkbox):
    BUTTON_INNER = " "
    def toggle(self) -> None:
        if self.value:
            CustomCheck.BUTTON_INNER = " "
        else:
            CustomCheck.BUTTON_INNER = "X"
        self.value = not self.value
        return self

class FoxHeadmakerApp(App):
    """A Textual app to compile heads for df usage."""
    CSS = """
    .collapsible-content {
        content-align: center middle;
    }

    .middlebar-container {
        background: $boost;
        height: 5;

        margin: 1;
        padding: 1;
    }

    .horizontal_group {
        background: $boost;

        margin: 1;
        padding: 1;
    }

    #headspritecontainer {
        background: $boost;
        height: 12;
        width: 19;

        margin: 1;
        padding: 1;
    }

    .middlebar {
        width: 1fr;
        height: 100%;

        content-align: center middle;
    }
    .loadingbartext {
        width: 3fr;
        content-align: center middle;
    }
    .loadingbar {
        width: 1fr;
        content-align: center middle;
    }

    .send_clipboard {
        color: #3cb1c8;
    }

    .send_millomod {
        color: #ff8137;
    }

    .send_codeclient {
        color: #ffa200;
    }

    .link {
        align: center middle;
    }

    #link_box {
        align: center middle;
    }

    #link_github {
        color: white;
        padding: 1;
        align: center middle;
    }

    #link_discord {
        color: #5562f6;
        padding: 1;
        align: center middle;
    }

    #link_twitch {
        color: #6441a5;
        padding: 1;
        align: center middle;
    }
    """
    AUTO_FOCUS = None
    def on_mount(self) -> None:
        self.title = "Fox's Headmaker"
        self.sub_title = "Compile textures for DF Styled Texts!"
    def get_system_commands(self, screen: Screen):
        yield from super().get_system_commands(screen)
        yield SystemCommand("Clear Head Cache","Clears the images generated by head compilation.",clear_cache)



    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Header()
        yield HorizontalGroup(
            Center(Link("GitHub",url="https://github.com/TheFoxPlush/FoxHeadmaker",classes="link",id="link_github")),
            Center(Link("Discord",url="https://discord.gg/xjpaRGCTgY",classes="link",id="link_discord")),
            Center(Link("Twitch",url="https://twitch.tv/thefoxplush",classes="link",id="link_twitch")),
            id="link_box"
        )
        with Collapsible(title="Mineskin.org API Key"):
            yield Input(placeholder="Enter your key here",password=True,select_on_focus=True,value=config.auth_key,classes="collapsible-content",id="input_auth_key")
            yield Link("How do I get a key?",url="https://account.mineskin.org/keys",classes="collapsible-content")
        self.current_spritesheet_path = None
        self.current_spritesheet_compiled = False
        self.item = None
        yield HorizontalGroup(
            Button("Load Spritesheet",id="choose_spritesheet",classes="middlebar"),
            Static("No file selected", id="result_spritesheet",classes="middlebar"),
            Button("Compile Heads",id="compile_heads",classes="middlebar"),
            Static("No heads compiled",id="result_compile_heads",classes="middlebar"),
            Button("Launch",variant="success",id="launch_requests",classes="middlebar"),
            CustomCheck("⛓️ Chain Mode",classes="middlebar",id="chain_mode"), #add later: \n[italic gray]Stitch together horizontally adjacent heads.[/]
            classes="middlebar-container horizontal_group"
        )
        yield HorizontalGroup(
            Static("[underline]🎨 Head texture[/]\n",classes="loadingbartext",id="loadingbar_headtexture"),LoadingIndicator(classes="loadingbar"),
            Static("[underline]💻 mineskin.org[/]\n",classes="loadingbartext",id="loadingbar_mineskin"),LoadingIndicator(classes="loadingbar"),
            Static("[underline]💾 Skin Value[/]\n",classes="loadingbartext",id="loadingbar_skinvalue"),
            classes="horizontal_group"
        )
        yield HorizontalGroup(
            Center(
            ProgressBar(
                id="progressbar"
            )
            ),
            classes="horizontal_group"
        )
        yield Static("🍎 Waiting for item...",id="item_indicator")
        yield HorizontalGroup(
            Button("📋 Copy give command to clipboard",classes="middlebar send_clipboard",id="send_clipboard"),
            Button("🙀 Send item to MilloMod",classes="middlebar send_millomod",id="send_millomod"),
            Button("⭐ Send item to CodeClient",classes="middlebar send_codeclient",id="send_codeclient"),
            classes="middlebar-container horizontal_group"
        )
        with Collapsible(title="Styled Text Extraction Function"):
            yield HorizontalGroup(
                Button("📋 Copy give command to clipboard",classes="middlebar send_clipboard",id="send_clipboard_function"),
                Button("🙀 Send template to MilloMod",classes="middlebar send_millomod",id="send_millomod_function"),
                Button("⭐ Send template to CodeClient",classes="middlebar send_codeclient",id="send_codeclient_function"),
                classes="middlebar-container horizontal_group"
            )


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "choose_spritesheet":
            self.push_screen(FilePicker(), self.spritesheet_chosen)
        elif event.button.id == "compile_heads":
            self.split_spritesheet()
        elif event.button.id == "launch_requests":
            self.launch_skinify_multiple()
        #sending the produced item
        elif event.button.id == "send_clipboard" or event.button.id == "send_millomod" or event.button.id == "send_codeclient":
            if not(app.item):
                app.notify("You need to have an item to send!",title="Error",severity="error")
                return
            if event.button.id == "send_clipboard":
                send_clipboard(app.item)
            elif event.button.id == "send_millomod":
                send_millomod(app.item_exports)
            elif event.button.id == "send_codeclient":
                send_codeclient(app.item_exports)
        #sending the function item
        elif event.button.id == "send_clipboard_function":
            send_clipboard(FUNCTION_ITEM)
        elif event.button.id == "send_millomod_function":
            send_millomod(FUNCTION_ITEM_EXPORTS)
        elif event.button.id == "send_codeclient_function":
            send_codeclient(FUNCTION_ITEM_EXPORTS)

    def on_input_blurred(self, event: Input.Blurred) -> None:
        if event.input.id == "input_auth_key":
            config.auth_key = event.input.value
            config.save()

    def reset_head_compilation(self) -> None:
        self.current_spritesheet_compiled = False
        self.query_one("#result_compile_heads", Static).update("No heads compiled")

    def on_paste(self,event) -> None: #for drag and drop
        if os.path.exists(event.text):
            self.spritesheet_chosen(event.text)

    def spritesheet_chosen(self, path: str | None) -> None:
        if path:
            if "@" in path:
                self.notify("Spritesheet path cannot contain @.",title="An error occured importing the spritesheet.",severity="error")
                return
            if not(path.endswith(".png")):
                self.notify("Spritesheet file must be .png.",title="An error occured importing the spritesheet.",severity="error")
                return
            self.current_spritesheet_path = path
            self.current_spritesheet_file = os.path.basename(self.current_spritesheet_path)
            self.current_spritesheet_name = os.path.splitext(self.current_spritesheet_file)[0]
            self.query_one("#result_spritesheet", Static).update(f"📄 {self.current_spritesheet_file}")
            self.reset_head_compilation()
    def split_spritesheet(self) -> None:
        self.current_head_files = []
        if self.current_spritesheet_path:
            try:
                with Image.open(self.current_spritesheet_path) as spritesheetfile:
                    max_x,max_y = spritesheetfile.size
                    if max_x%8!=0 or max_y%8!=0: #check that dimensions are *8
                        raise(ValueError(f"Spritesheet's dimensions must be multiples of 8, not ({max_x}*{max_y})"))
                    max_x//=8
                    max_y//=8
                    head_id = 0
                    for y in range(max_y):
                        heads_in_a_row = -1
                        for x in range(max_x):
                            tile = spritesheetfile.crop((x*8,y*8,(x+1)*8,(y+1)*8))
                            if not tile.getbbox(): #hack to detect if image is fully empty
                                heads_in_a_row = -1
                                continue
                            head_id+=1
                            heads_in_a_row+=1
                            HEAD_TEMPLATE.paste(tile,(8,8))
                            HEAD_TEMPLATE.save(os.path.join(CACHE_HEADS_DIR,f"{self.current_spritesheet_name}@{head_id}@{heads_in_a_row}.png"))
                            self.current_head_files.append(f"{self.current_spritesheet_name}@{head_id}@{heads_in_a_row}.png")
                self.query_one("#result_compile_heads", Static).update(f"👤 Found {head_id} Heads")
                self.current_spritesheet_compiled = True
                self.query_one('#progressbar',ProgressBar).total = head_id
            except Exception as e:
                self.notify(f"{e}.",severity="error",title="An error occured during compilation.")
        else:
            self.notify("A spritesheet needs to be loaded before you compile.",severity="error")

    def launch_skinify_multiple(self):
        if not(self.current_spritesheet_compiled):
            self.notify("You must have succesfully compiled heads before launching.",severity="error")
            return
        if config.auth_key == "":
            self.notify("You must define a mineskin.org API Key.",severity="error")
            return
        thread(target=skinify_multiple,args=(self.current_head_files,)).start()

if __name__ == "__main__":
    global config,app
    config = Config()
    config.save()
    app = FoxHeadmakerApp()
app.run()