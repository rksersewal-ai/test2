@echo off
REM =============================================================================
REM FILE: deployment/update_edms.bat
REM Pull latest code from GitHub and redeploy without reinstalling services.
REM Run as Administrator whenever you push changes to the repo.
REM
REM BUG FIX #10: NGINX_DIR was never defined in this file (it was only set in
REM   install_services.bat). The nginx reload silently failed on every update.
REM   Added set NGINX_DIR=C:\nginx at top of script.
REM =============================================================================

setlocal

set PROJECT_DIR=D:\plw_edms
set PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe
set NSSM=nssm
set NGINX_DIR=C:\nginx

echo ============================================================
echo  PLW EDMS - Update Deployment
echo ============================================================
echo.

cd /d %PROJECT_DIR%

if not exist "%PYTHON%" (
    echo [ERROR] Venv not found. Run install_services.bat first.
    pause & exit /b 1
)

echo [1/6] Pulling latest code from GitHub...
git pull origin main
if errorlevel 1 (
    echo [ERROR] git pull failed. Check network or merge conflicts.
    pause & exit /b 1
)

echo [2/6] Installing/updating Python dependencies...
%PYTHON% -m pip install -r requirements.txt --quiet
if errorlevel 1 ( echo [ERROR] pip install failed & pause & exit /b 1 )

echo [3/6] Stopping backend service...
%NSSM% stop EDMS-Backend
timeout /t 3 /nobreak >nul

echo [4/6] Running database migrations...
set DJANGO_SETTINGS_MODULE=config.settings.production
%PYTHON% manage.py migrate --noinput
if errorlevel 1 ( echo [ERROR] Migrations failed & pause & exit /b 1 )

echo [5/6] Collecting static files...
%PYTHON% manage.py collectstatic --noinput
if errorlevel 1 ( echo [ERROR] collectstatic failed & pause & exit /b 1 )

echo [6/6] Restarting services...
%NSSM% start EDMS-Backend
timeout /t 2 /nobreak >nul

REM BUG FIX #10: NGINX_DIR is now defined above — reload always works
"%NGINX_DIR%\nginx.exe" -s reload
if errorlevel 1 (
    echo [WARN] Nginx reload failed — check nginx config syntax:
    echo        %NGINX_DIR%\nginx.exe -t
)

echo.
echo ============================================================
echo  Update complete! EDMS is running with latest code.
echo  Check logs at: %PROJECT_DIR%\logs\waitress_stderr.log
echo ============================================================
pause
