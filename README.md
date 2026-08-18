# Server Launcher (Prime Rebar)

Windows app for opening Prime Rebar project folders on `Z:\Projects`.

## Download for Windows

**[Download ServerLauncherPR-windows.zip](https://github.com/vishalprime20/ServerLauncherPR/releases/latest)**

1. Download `ServerLauncherPR-windows.zip`.
2. Right-click the zip → **Properties** → tick **Unblock** → **Apply**.
3. Extract the zip.
4. Open `ServerLauncherPR\ServerLauncherPR.exe` with a normal double-click (not Run as administrator).

Windows Defender may warn that an unsigned Python app is unwanted software. That is a false positive. If it blocks the file: **Windows Security → Virus & threat protection → Protection history → Allow on device**. You can also add an exclusion for the extracted `ServerLauncherPR` folder.

## Run from source

```bat
cd ServerLauncherPython
python -m pip install -r requirements.txt
python server_launcher.py
```

Python 3.10+ with tkinter is required. On Windows, install Python from [python.org](https://www.python.org/downloads/) and keep **tcl/tk** enabled.
