@echo off
:: =============================================================================
:: FILE: scripts/start_frontend.bat
:: EDMS-LDO — Start Vite frontend dev server on port 4173
:: Double-click to run, or call from start_edms.bat
:: =============================================================================
title EDMS Frontend (Port 4173)
color 0B

echo ============================================================
echo  EDMS-LDO Frontend Starting...
echo  Port  : 4173
echo  URL   : http://localhost:4173
echo  Proxy : /api  -> http://127.0.0.1:8765
echo ============================================================
echo.

:: Check port 4173 is free
netstat -ano | findstr :4173 >nul 2>&1
if %errorlevel%==0 (
    echo [WARNING] Port 4173 is already in use!
    pause
    exit /b 1
)

:: Navigate to frontend directory
cd /d "%~dp0..\"
cd frontend

:: Check node_modules exists
if not exist "node_modules" (
    echo node_modules not found. Running npm install...
    npm install
    if %errorlevel% neq 0 (
        echo [ERROR] npm install failed.
        pause
        exit /b 1
    )
)

:: Create .env.local if missing
if not exist ".env.local" (
    if exist ".env.example" (
        echo Creating .env.local from .env.example...
        copy .env.example .env.local
    )
)

echo Starting Vite on port 4173...
echo Press Ctrl+C to stop.
echo.
npm run dev
pause
