@echo off
:: =============================================================================
:: FILE: scripts/start_backend.bat
:: EDMS-LDO — Start Django backend on port 8765
:: Double-click to run, or call from start_edms.bat
:: =============================================================================
title EDMS Backend (Port 8765)
color 0A

echo ============================================================
echo  EDMS-LDO Backend Starting...
echo  Port : 8765
echo  URL  : http://localhost:8765/api/v1/
echo  Admin: http://localhost:8765/admin/
echo ============================================================
echo.

:: Check port 8765 is free
netstat -ano | findstr :8765 >nul 2>&1
if %errorlevel%==0 (
    echo [WARNING] Port 8765 is already in use!
    echo Check running processes: netstat -ano ^| findstr :8765
    pause
    exit /b 1
)

:: Navigate to backend directory
cd /d "%~dp0..\"
cd backend

:: Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found at backend\venv\
    echo Run: python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

:: Load .env if present
if exist ".env" (
    echo Loading .env configuration...
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if not "%%A"=="" if not "%%A:~0,1%%"=="#" set "%%A=%%B"
    )
)

:: Run migrations silently (safe to run on every start)
echo Running database migrations...
python manage.py migrate --run-syncdb 2>&1

:: Start server
echo.
echo Starting Django on 0.0.0.0:8765 ...
echo Press Ctrl+C to stop.
echo.
python manage.py runserver 0.0.0.0:8765
pause
