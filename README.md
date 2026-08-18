# Server Launcher (Prime Rebar)

Windows app for opening Prime Rebar project folders on `Z:\Projects`.

## Download for Windows

**[Download ServerLauncherPR.exe](https://github.com/vishalprime20/ServerLauncherPR/releases/latest)**

1. Open the latest release.
2. Download `ServerLauncherPR.exe`.
3. Run the file (Windows may show a SmartScreen prompt for a new unsigned app — choose **More info** → **Run anyway**).

## Run from source

```bat
cd ServerLauncherPython
python -m pip install -r requirements.txt
python server_launcher.py
```

Python 3.10+ with tkinter is required. On Windows, install Python from [python.org](https://www.python.org/downloads/) and keep **tcl/tk** enabled.
