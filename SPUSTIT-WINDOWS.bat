@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 server.py
  pause
  exit /b
)
python --version >nul 2>nul
if %errorlevel% equ 0 (
  python server.py
  pause
  exit /b
)
echo Pro spusteni je potreba Python 3 z python.org.
pause
