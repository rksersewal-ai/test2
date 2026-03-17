@echo off
REM PLW EDMS - Start all services
REM Run as Administrator

echo ============================================
echo  PLW EDMS + LDO - Start Services
echo ============================================

set PROJECT_DIR=D:\plw_edms
set PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe
set DJANGO_SETTINGS_MODULE=config.settings.production

cd /d %PROJECT_DIR%

if not exist .env goto :missing_env
if not exist "%PYTHON%" goto :missing_python
if not exist logs mkdir logs
if not exist media mkdir media
if not exist staticfiles mkdir staticfiles

echo [1/4] Running migrations...
%PYTHON% manage.py migrate --noinput
if errorlevel 1 goto :error

echo [2/4] Collecting static files...
%PYTHON% manage.py collectstatic --noinput
if errorlevel 1 goto :error

echo [3/4] Starting OCR worker via Task Scheduler...
schtasks /Run /TN "PLW-EDMS-OCR-Worker"

echo [4/4] Starting EDMS application server (Waitress)...
start "PLW-EDMS-App" %PYTHON% deployment\waitress_server.py

echo.
echo  EDMS is now running.
echo  Access at: https://your-configured-hostname-or-LAN-IP
echo.
pause
goto :eof

:missing_env
echo.
echo  ERROR: .env not found in %PROJECT_DIR%.
echo  Copy .env.example to .env and fill the production values first.
pause
exit /b 1

:missing_python
echo.
echo  ERROR: Python virtual environment not found at %PYTHON%.
echo  Create it with: python -m venv venv
pause
exit /b 1

:error
echo.
echo  ERROR: Startup failed. Check logs\waitress.log for details.
pause
exit /b 1
