@echo off
setlocal
cd /d "%~dp0"

python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onedir --windowed --noupx ^
  --name ServerLauncherPR ^
  --icon assets\icon.ico ^
  --version-file file_version_info.txt ^
  --hidden-import PIL ^
  --add-data "assets\logo_compact.gif;assets" ^
  --add-data "assets\logo_preview.png;assets" ^
  --add-data "assets\logo_ui.png;assets" ^
  --add-data "assets\icon.ico;assets" ^
  --add-data "assets\icon.png;assets" ^
  server_launcher.py

echo.
echo Built: dist\ServerLauncherPR\ServerLauncherPR.exe
endlocal
