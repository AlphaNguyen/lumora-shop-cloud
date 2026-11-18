@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo =============================================
echo     LUMORA SHOP - DE TAI 18 - LOCAL DEMO
echo =============================================
where py >nul 2>nul
if %errorlevel%==0 (set "PY_CMD=py -3") else (set "PY_CMD=python")
if not exist ".venv\Scripts\python.exe" (
    %PY_CMD% -m venv .venv
    if errorlevel 1 (echo LOI: Can cai Python 3.11 hoac 3.12 va chon Add to PATH.&pause&exit /b 1)
)
if not exist ".venv\.installed" (
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (echo LOI: Can ket noi Internet de cai thu vien.&pause&exit /b 1)
    echo ok > .venv\.installed
)
if not exist ".local-secret" (
    .venv\Scripts\python.exe -c "import secrets;open('.local-secret','w').write(secrets.token_urlsafe(48))"
)
set /p SECRET_KEY=<.local-secret
set "DATABASE_URL=sqlite:///./lumora.db"
set "ENABLE_DEMO_ACCOUNTS=1"
set "APP_ENV=development"
echo.
echo Dia chi mo tren trinh duyet: http://127.0.0.1:8000
start "" "http://127.0.0.1:8000"
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
