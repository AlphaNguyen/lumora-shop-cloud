@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Hay chay CHAY_NHANH_WINDOWS.bat truoc de cai thu vien.
 pause
 exit /b 1
)
.venv\Scripts\python.exe -m pip install pytest httpx
.venv\Scripts\python.exe -m pytest -q
pause
