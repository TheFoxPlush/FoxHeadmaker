from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Header, Input, Collapsible, Link, Button, DirectoryTree, Static, LoadingIndicator, ProgressBar
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
            Static("Select a file"),
            DirectoryTree(config.last_file_dialog),
        )
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.dismiss(str(event.path))
        config.last_file_dialog = str(event.path.parent)
        config.save()

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
    for head_file in current_head_files:
        with Image.open(CACHE_HEADS_DIR+"/"+head_file,"r") as skin_image:
            head_image = skin_image.crop((8,8,16,16))
            app.query_one("#loadingbar_headtexture",Static).update(f"[underline]🎨 Head texture[/]\n{image_to_static_text(head_image)}")
        app.query_one("#loadingbar_mineskin",Static).update(f"[underline]💻 mineskin.org[/]\n[italic gray]Waiting for response...[/]")
        app.query_one("#loadingbar_skinvalue",Static).update(f"[underline]💾 Skin Value[/]\n[italic gray]Waiting for response...[/]")
        value = skinify(f"{CACHE_HEADS_DIR}/{head_file}",f"{app.current_spritesheet_name}_{head_file}")
        values[f"{app.current_spritesheet_name}_{head_file}"] = value
        save_values(values,app.current_spritesheet_name)
        app.query_one('#progressbar',ProgressBar).advance(1)
    make_item(app.current_spritesheet_name)

def make_item(name,mode="singles_only"): #"singles_only" or "chains"
    try:
        with open(f"{CACHE_VALUES_DIR}/{name}.json","r") as valuesfile:
            values = json_load(valuesfile)
        lore = []
        for key,value in values.items():
            chain = False
            line = '{player:{properties:[{name:"textures",value:"'+value+'"}]}}'
            lore.append(line)
        lore = "["+",".join(lore)+"]"
        app.item = 'apple[lore='+lore+',custom_name={"color":"#FFA200","italic":false,"shadow_color":-10341322,"text":"'+name+'"}]'
        app.item_exports = '{count:1,id:"minecraft:apple",components:{"custom_name":{"color":"#FFA200","italic":false,"shadow_color":-10341322,"text":"'+name+'"},"lore":'+lore+'}}'
        app.query_one('#item_indicator',Static).update(f"🍎 Item '{name}' is ready!")
    except Exception as e:
        app.notify(f"{e}",title="Error in item compilation: Contact TheFoxPlush",severity="error")

def send_clipboard():
    pyperclip_copy(f"/give @p {app.item} 1")
    app.notify("Give command copied to clipboard",title="Success!")

def send_millomod():
    with connect("ws://localhost:31321") as websocket:
        websocket.send(json_dumps({"type":"item","source":"FoxHeadmaker","data":f"{app.item_exports}"}))
    app.notify("Item sent to MilloMod",title="Success!")

def send_codeclient():
    try:
        with connect("ws://localhost:31375") as websocket:
            websocket.send(f"give {app.item_exports}")
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
            app.notify(f"Response status code: {response.status_code}. Trying again in 5s...",title="An error occured during the process.",severity="error")
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

    HorizontalGroup {
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

    #send_clipboard {
        color: #3cb1c8;
    }

    #send_millomod {
        color: #ff8137;
    }

    #send_codeclient {
        color: #ffa200;
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
            classes="middlebar-container"
        )
        yield HorizontalGroup(
            Static("[underline]🎨 Head texture[/]\n",classes="loadingbartext",id="loadingbar_headtexture"),LoadingIndicator(classes="loadingbar"),
            Static("[underline]💻 mineskin.org[/]\n",classes="loadingbartext",id="loadingbar_mineskin"),LoadingIndicator(classes="loadingbar"),
            Static("[underline]💾 Skin Value[/]\n",classes="loadingbartext",id="loadingbar_skinvalue")
        )
        yield HorizontalGroup(
            Center(
            ProgressBar(
                id="progressbar"
            )
            )
        )
        yield Static("🍎 Waiting for item...",id="item_indicator")
        yield HorizontalGroup(
            Button("📋 Copy give command to clipboard",classes="middlebar",id="send_clipboard"),
            Button("🙀 Send item to MilloMod",classes="middlebar",id="send_millomod"),
            Button("⭐ Send item to CodeClient",classes="middlebar",id="send_codeclient"),
            classes="middlebar-container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "choose_spritesheet":
            self.push_screen(FilePicker(), self.spritesheet_chosen)
        elif event.button.id == "compile_heads":
            self.split_spritesheet()
        elif event.button.id == "launch_requests":
            self.launch_skinify_multiple()
        elif event.button.id == "send_clipboard" or event.button.id == "send_millomod" or event.button.id == "send_codeclient":
            if not(app.item):
                app.notify("You need to have an item to send!",title="Error",severity="error")
                return
            if event.button.id == "send_clipboard":
                send_clipboard()
            elif event.button.id == "send_millomod":
                send_millomod()
            elif event.button.id == "send_codeclient":
                send_codeclient()

    def on_input_blurred(self, event: Input.Blurred) -> None:
        if event.input.id == "input_auth_key":
            config.auth_key = event.input.value
            config.save()

    def reset_head_compilation(self) -> None:
        self.current_spritesheet_compiled = False
        self.query_one("#result_compile_heads", Static).update("No heads compiled")


    def spritesheet_chosen(self, path: str | None) -> None:
        if path:
            if "@" in path:
                self.query_one("#result_spritesheet", Static).update(f"❌ Spritesheet path cannot contain @.")
                return
            self.current_spritesheet_path = path
            self.current_spritesheet_file = self.current_spritesheet_path.split("\\")[-1]
            self.current_spritesheet_name = ".".join(self.current_spritesheet_file.split(".")[:-1])
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