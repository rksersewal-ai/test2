@echo off
REM PLW EDMS - PostgreSQL backup script
REM Schedule via Task Scheduler to run daily at 02:00

set BACKUP_DIR=D:\plw_edms_backups
set PG_DUMP=C:\Program Files\PostgreSQL\15\bin\pg_dump.exe
set DB_NAME=plw_edms_db
set DB_USER=plw_edms_user
set PGPASSWORD=YOUR_DB_PASSWORD_HERE

REM Create timestamped filename
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set DT=%%I
set BACKUP_FILE=%BACKUP_DIR%\plw_edms_%DT:~0,8%_%DT:~8,6%.dump

REM Ensure backup directory exists
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo [%date% %time%] Starting backup to %BACKUP_FILE%

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
