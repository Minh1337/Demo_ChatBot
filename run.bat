@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist .venv\Scripts\python.exe (
  echo Environment not found. Run setup.bat first.
  pause
  exit /b 1
)
echo Starting PyBan at http://127.0.0.1:8765/
echo Keep this window open. Stop the server with Ctrl+C.
.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8765
pause
