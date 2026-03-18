@echo off
REM PLW EDMS - PostgreSQL backup script
REM Schedule via Task Scheduler to run daily at 02:00

set "BACKUP_DIR=D:\plw_edms_backups"
set "PG_BIN_DIR=C:\Program Files\PostgreSQL\18\bin"
set "PG_DUMP="
set "DB_NAME=plw_edms_db"
set "DB_USER=plw_edms_user"
set "PGPASSWORD=YOUR_DB_PASSWORD_HERE"

if exist "%PG_BIN_DIR%\pg_dump.exe" set "PG_DUMP=%PG_BIN_DIR%\pg_dump.exe"

if not defined PG_DUMP (
    for /f "delims=" %%I in ('where pg_dump.exe 2^>nul') do if not defined PG_DUMP set "PG_DUMP=%%I"
)

if not defined PG_DUMP (
    echo [%date% %time%] pg_dump.exe not found. Set PG_BIN_DIR or add PostgreSQL 18\bin to PATH.
    exit /b 1
)

REM Create timestamped filename
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set DT=%%I
set BACKUP_FILE=%BACKUP_DIR%\plw_edms_%DT:~0,8%_%DT:~8,6%.dump

REM Ensure backup directory exists
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo [%date% %time%] Starting backup with %PG_DUMP% to %BACKUP_FILE%

"%PG_DUMP%" -U %DB_USER% -h localhost -p 5432 -Fc %DB_NAME% -f "%BACKUP_FILE%"

if errorlevel 1 (
    echo [%date% %time%] BACKUP FAILED >> %BACKUP_DIR%\backup.log
    exit /b 1
) else (
    echo [%date% %time%] Backup successful: %BACKUP_FILE% >> %BACKUP_DIR%\backup.log
)

REM Delete backups older than 30 days
forfiles /p "%BACKUP_DIR%" /s /m *.dump /d -30 /c "cmd /c del @path" 2>nul

echo Backup complete.
