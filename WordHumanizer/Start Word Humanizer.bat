@echo off
setlocal
title Word Humanizer
cd /d "%~dp0"

rem ---- Find Python ------------------------------------------------------------
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY goto nopython
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul || goto nopython

rem ---- First run: create the environment and install the libraries -----------
if exist "venv\Scripts\python.exe" goto installed
echo.
echo  First start: setting up Word Humanizer. This takes 1-2 minutes...
echo.
%PY% -m venv venv || goto failed
:installed
"venv\Scripts\python.exe" -c "import docx, fastapi, uvicorn, requests, dotenv, tenacity, multipart" >nul 2>nul && goto ready
echo  Installing the required libraries...
"venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt || goto failed

:ready
if not exist ".env" copy ".env.example" ".env" >nul

rem ---- Start ------------------------------------------------------------------
echo.
echo  ==============================================================
echo    Word Humanizer is running at  http://localhost:8000
echo    Your browser will open automatically.
echo    Keep this window open while you use it. Close it to stop.
echo  ==============================================================
echo.
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 4; Start-Process 'http://localhost:8000'"
"venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000
echo.
echo  Word Humanizer stopped.
pause
exit /b 0

:nopython
echo.
echo  Python 3.10 or newer was not found.
echo  1. Download it from https://www.python.org/downloads/
echo  2. In the installer, tick "Add Python to PATH", then click Install.
echo  3. Double-click this file again.
echo.
start "" https://www.python.org/downloads/
pause
exit /b 1

:failed
echo.
echo  Setup failed - see the messages above. Check your internet connection,
echo  delete the "venv" folder, and double-click this file again.
echo.
pause
exit /b 1
