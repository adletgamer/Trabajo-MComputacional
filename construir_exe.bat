@echo off
rem Genera dist\ComponentesConexas.exe (requiere Python con Tkinter e internet para instalar PyInstaller)
cd /d "%~dp0"
if not exist .venv ( python -m venv .venv || py -m venv .venv )
.venv\Scripts\python.exe -m pip install --quiet pyinstaller
.venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --windowed --name ComponentesConexas main.py
echo.
echo Listo: dist\ComponentesConexas.exe
pause
