@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found. Install Python 3.10 or newer and enable Add Python to PATH.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo Setup complete. Start the app with run.bat.
pause
exit /b 0
:failed
echo Setup failed. Check the Python installation and internet connection, then try again.
pause
exit /b 1
