@echo off
:: =============================================================================
:: FILE: scripts/stop_edms.bat
:: EDMS-LDO — Stop all EDMS services by killing processes on ports 8765 + 4173
:: =============================================================================
title EDMS-LDO Stop
color 0C

echo Stopping EDMS services on ports 8765 and 4173...
echo.

:: Kill port 8765 (Django)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8765') do (
    echo Killing PID %%a on port 8765...
    taskkill /PID %%a /F >nul 2>&1
)

:: Kill port 4173 (Vite)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :4173') do (
    echo Killing PID %%a on port 4173...
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo EDMS services stopped.
pause
