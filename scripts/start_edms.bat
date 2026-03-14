@echo off
:: =============================================================================
:: FILE: scripts/start_edms.bat
:: EDMS-LDO — Master launcher
:: Starts backend (8765) and frontend (4173) in separate windows.
:: Double-click this file to start the entire application.
:: =============================================================================
title EDMS-LDO Launcher
color 0E

echo.
echo  ########################################
echo  #   EDMS-LDO Application Launcher     #
echo  ########################################
echo.
echo  Starting services...
echo  Backend  : http://localhost:8765
echo  Frontend : http://localhost:4173
echo.
echo  NOTE: Port 8000 avoided (DSC Signer conflict)
echo.

:: Start backend in a new window
start "EDMS Backend" cmd /k "%~dp0start_backend.bat"

:: Wait 3 seconds for Django to initialise before starting frontend
timeout /t 3 /nobreak >nul

:: Start frontend in a new window
start "EDMS Frontend" cmd /k "%~dp0start_frontend.bat"

:: Wait then open browser
timeout /t 5 /nobreak >nul
echo Opening browser...
start http://localhost:4173

echo.
echo Both services launched in separate windows.
echo Close those windows or press Ctrl+C in each to stop.
pause
