@echo off
REM =============================================================================
REM FILE: deployment/build_frontend.bat
REM Builds the React/Vite frontend and copies dist to C:\EDMS\frontend\dist
REM so Nginx can serve it as static files.
REM
REM Run this after any frontend code changes, OR it is called automatically
REM by update_edms.bat if frontend files changed.
REM =============================================================================

setlocal

set PROJECT_DIR=D:\plw_edms
set FRONTEND_DIR=%PROJECT_DIR%\frontend
set DIST_TARGET=C:\EDMS\frontend\dist

echo ============================================================
echo  PLW EDMS - Build React Frontend
echo ============================================================

cd /d "%FRONTEND_DIR%"

if not exist node_modules (
    echo [1/2] Installing npm dependencies...
    npm install
    if errorlevel 1 ( echo [ERROR] npm install failed & pause & exit /b 1 )
) else (
    echo [1/2] node_modules present, skipping npm install.
)

echo [2/2] Building production bundle...
set VITE_API_BASE_URL=/api/v1
npm run build
if errorlevel 1 ( echo [ERROR] Vite build failed & pause & exit /b 1 )

echo Copying dist to %DIST_TARGET%...
if not exist "%DIST_TARGET%" mkdir "%DIST_TARGET%"
xcopy /E /I /Y "%FRONTEND_DIR%\dist\*" "%DIST_TARGET%\"

echo.
echo [OK] Frontend built and deployed to %DIST_TARGET%
echo      Nginx will serve it at https://your-server/
pause
