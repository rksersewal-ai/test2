@echo off
:: =============================================================================
:: FILE: scripts/check_ports.bat
:: Check which processes are using EDMS ports before starting
:: =============================================================================
title EDMS Port Check

echo ============================================================
echo  EDMS-LDO Port Status Check
echo ============================================================
echo.

echo [PORT 8765 - EDMS Backend]
netstat -ano | findstr :8765
if %errorlevel% neq 0 echo   FREE - safe to start backend
echo.

echo [PORT 4173 - EDMS Frontend]
netstat -ano | findstr :4173
if %errorlevel% neq 0 echo   FREE - safe to start frontend
echo.

echo [PORT 8000 - DSC Signer (should be occupied)]
netstat -ano | findstr :8000
if %errorlevel% neq 0 echo   FREE (DSC Signer not running)
echo.

echo [PORT 5432 - PostgreSQL]
netstat -ano | findstr :5432
if %errorlevel% neq 0 echo   FREE (PostgreSQL not running - start it first!)
echo.

pause
