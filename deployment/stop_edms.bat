@echo off
REM PLW EDMS - Stop all services
REM Run as Administrator

echo ============================================
echo  PLW EDMS + LDO - Stop Services
echo ============================================

echo Stopping OCR worker...
schtasks /End /TN "PLW-EDMS-OCR-Worker"

echo Stopping Waitress app server...
taskkill /F /FI "WINDOWTITLE eq PLW-EDMS-App" /T

echo All PLW EDMS services stopped.
pause
