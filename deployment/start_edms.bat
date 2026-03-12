@echo off
REM PLW EDMS - Start all services
REM Run as Administrator

echo ============================================
echo  PLW EDMS + LDO - Start Services
echo ============================================

set PROJECT_DIR=D:\plw_edms
set PYTHON=C:\Python311\python.exe
set DJANGO_SETTINGS_MODULE=config.settings.production

cd /d %PROJECT_DIR%

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
echo  Access at: http://192.168.1.100  (or your configured LAN IP)
echo.
pause
goto :eof

:error
echo.
echo  ERROR: Startup failed. Check logs\waitress.log for details.
pause
exit /b 1
