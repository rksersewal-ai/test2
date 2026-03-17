@echo off
REM =============================================================================
REM FILE: deployment/install_services.bat
REM One-time setup: installs EDMS-Backend and Nginx as Windows Services via NSSM.
REM Run ONCE as Administrator on first deployment.
REM
REM Prerequisites:
 REM   1. NSSM installed: https://nssm.cc/download  (add to PATH or place at C:\nssm\nssm.exe)
REM   2. Python venv created: python -m venv D:\plw_edms\venv
REM   3. Dependencies installed: venv\Scripts\pip install -r requirements.txt
REM   4. Nginx for Windows: https://nginx.org/en/download.html  extracted to C:\nginx
REM   5. .env file created from .env.example and filled with production values
REM   6. SSL cert placed at C:\nginx\ssl\edms.crt and C:\nginx\ssl\edms.key
REM =============================================================================

setlocal

set PROJECT_DIR=D:\plw_edms
set PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe
set NSSM=nssm
set NGINX_DIR=C:\nginx

echo ============================================================
echo  PLW EDMS - Install Windows Services (Run as Administrator)
echo ============================================================
echo.

REM --- Validate prerequisites ---
if not exist "%PYTHON%" (
    echo [ERROR] Python venv not found at %PYTHON%
    echo         Run: python -m venv %PROJECT_DIR%\venv
    pause & exit /b 1
)
if not exist "%PROJECT_DIR%\.env" (
    echo [ERROR] .env file missing. Copy .env.example to .env and fill values.
    pause & exit /b 1
)
if not exist "%NGINX_DIR%\nginx.exe" (
    echo [ERROR] Nginx not found at %NGINX_DIR%\nginx.exe
    echo         Download from https://nginx.org/en/download.html
    pause & exit /b 1
)

REM --- Copy nginx config ---
echo [1/5] Copying nginx config...
copy /Y "%PROJECT_DIR%\deployment\nginx_windows.conf" "%NGINX_DIR%\conf\nginx.conf"
if errorlevel 1 ( echo [ERROR] Failed to copy nginx.conf & pause & exit /b 1 )

REM --- Run Django setup ---
echo [2/5] Running migrations and collectstatic...
cd /d %PROJECT_DIR%
set DJANGO_SETTINGS_MODULE=config.settings.production
%PYTHON% manage.py migrate --noinput
if errorlevel 1 ( echo [ERROR] Migrations failed & pause & exit /b 1 )
%PYTHON% manage.py collectstatic --noinput
if errorlevel 1 ( echo [ERROR] collectstatic failed & pause & exit /b 1 )

REM --- Remove old services if they exist ---
echo [3/5] Removing existing services (if any)...
%NSSM% stop  EDMS-Backend 2>nul
%NSSM% remove EDMS-Backend confirm 2>nul
%NSSM% stop  EDMS-Nginx 2>nul
%NSSM% remove EDMS-Nginx confirm 2>nul

REM --- Install Waitress backend service ---
echo [4/5] Installing EDMS-Backend service (Waitress)...
%NSSM% install EDMS-Backend "%PYTHON%" "deployment\waitress_server.py"
%NSSM% set EDMS-Backend AppDirectory "%PROJECT_DIR%"
%NSSM% set EDMS-Backend AppEnvironmentExtra "DJANGO_SETTINGS_MODULE=config.settings.production"
%NSSM% set EDMS-Backend AppStdout "%PROJECT_DIR%\logs\waitress_stdout.log"
%NSSM% set EDMS-Backend AppStderr "%PROJECT_DIR%\logs\waitress_stderr.log"
%NSSM% set EDMS-Backend AppRotateFiles 1
%NSSM% set EDMS-Backend AppRotateBytes 10485760
%NSSM% set EDMS-Backend Start SERVICE_AUTO_START
%NSSM% set EDMS-Backend ObjectName LocalSystem
%NSSM% start EDMS-Backend
if errorlevel 1 ( echo [ERROR] Failed to start EDMS-Backend service & pause & exit /b 1 )

REM --- Install Nginx service ---
echo [5/5] Installing EDMS-Nginx service...
%NSSM% install EDMS-Nginx "%NGINX_DIR%\nginx.exe"
%NSSM% set EDMS-Nginx AppDirectory "%NGINX_DIR%"
%NSSM% set EDMS-Nginx AppStdout "%NGINX_DIR%\logs\nginx_stdout.log"
%NSSM% set EDMS-Nginx AppStderr "%NGINX_DIR%\logs\nginx_stderr.log"
%NSSM% set EDMS-Nginx Start SERVICE_AUTO_START
%NSSM% start EDMS-Nginx
if errorlevel 1 ( echo [ERROR] Failed to start EDMS-Nginx service & pause & exit /b 1 )

echo.
echo ============================================================
echo  Services installed and started successfully!
echo  EDMS-Backend : Waitress on 127.0.0.1:8765
echo  EDMS-Nginx   : Nginx on port 80/443
echo.
echo  Access at: https://192.168.1.100  (or your server IP)
echo  Admin at:  https://192.168.1.100/admin/
echo ============================================================
pause
