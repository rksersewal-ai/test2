<#
.SYNOPSIS
    Nightly PostgreSQL backup for PLW EDMS database.

.DESCRIPTION
    Runs pg_dump in custom format (-Fc), stores dated dump files in
    D:\edms_backups\ and deletes files older than 30 days.

    SCHEDULE (Windows Task Scheduler):
      - Trigger:  Daily at 02:00 AM
      - Action:   powershell.exe -NonInteractive -File "C:\edms\scripts\backup_db.ps1"
      - Run As:   Local System or a service account with pg_dump access

    CONFIGURATION:
      Edit the variables in the CONFIG section below.
      Alternatively set environment variables with the same names.

    RESTORE:
      pg_restore -U edms_user -d edms_ldo -Fc D:\edms_backups\edms_20260318.dump
#>

# ---- CONFIG -----------------------------------------------------------------
$PG_HOST     = if ($env:DB_HOST)     { $env:DB_HOST }     else { 'localhost' }
$PG_PORT     = if ($env:DB_PORT)     { $env:DB_PORT }     else { '5432' }
$PG_USER     = if ($env:DB_USER)     { $env:DB_USER }     else { 'edms_user' }
$PG_DB       = if ($env:DB_NAME)     { $env:DB_NAME }     else { 'edms_ldo' }
$PGPASSWORD  = if ($env:DB_PASSWORD) { $env:DB_PASSWORD } else { '' }
$BACKUP_DIR  = if ($env:BACKUP_DIR)  { $env:BACKUP_DIR }  else { 'D:\edms_backups' }
$RETAIN_DAYS = 30
$PG_DUMP     = if ($env:PG_DUMP_EXE) { $env:PG_DUMP_EXE } else {
                   'C:\Program Files\PostgreSQL\16\bin\pg_dump.exe'
               }
# -----------------------------------------------------------------------------

$ErrorActionPreference = 'Stop'

# Ensure backup directory exists
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
    Write-Host "[INFO] Created backup directory: $BACKUP_DIR"
}

$Date       = Get-Date -Format 'yyyyMMdd_HHmm'
$BackupFile = Join-Path $BACKUP_DIR "edms_${Date}.dump"
$LogFile    = Join-Path $BACKUP_DIR "backup_${Date}.log"

Write-Host "[$(Get-Date)] Starting backup of $PG_DB to $BackupFile"

# Set password via environment (pg_dump reads PGPASSWORD)
$env:PGPASSWORD = $PGPASSWORD

try {
    $args = @(
        '--host',     $PG_HOST,
        '--port',     $PG_PORT,
        '--username', $PG_USER,
        '--dbname',   $PG_DB,
        '--format',   'c',         # custom format — fastest, smallest, restores in parallel
        '--compress', '6',         # gzip level 6 — good balance of speed vs size
        '--file',     $BackupFile
    )
    & $PG_DUMP @args 2>&1 | Tee-Object -FilePath $LogFile

    if ($LASTEXITCODE -ne 0) {
        throw "pg_dump exited with code $LASTEXITCODE. Check $LogFile for details."
    }

    $SizeMB = [math]::Round((Get-Item $BackupFile).Length / 1MB, 2)
    Write-Host "[$(Get-Date)] Backup completed: $BackupFile ($SizeMB MB)"

} catch {
    Write-Error "[$(Get-Date)] BACKUP FAILED: $_"
    # Write failure marker file so monitoring scripts can detect it
    Set-Content -Path (Join-Path $BACKUP_DIR 'BACKUP_FAILED') -Value "$Date: $_"
    exit 1
} finally {
    $env:PGPASSWORD = ''   # clear from environment after use
}

# ---- RETENTION: delete backups older than RETAIN_DAYS ----------------------
Write-Host "[$(Get-Date)] Cleaning up backups older than $RETAIN_DAYS days..."
$cutoff = (Get-Date).AddDays(-$RETAIN_DAYS)
$deleted = 0

Get-ChildItem -Path $BACKUP_DIR -Filter '*.dump' | Where-Object {
    $_.LastWriteTime -lt $cutoff
} | ForEach-Object {
    Write-Host "[CLEANUP] Deleting old backup: $($_.Name)"
    Remove-Item $_.FullName -Force
    $deleted++
}

# Also clean corresponding log files
Get-ChildItem -Path $BACKUP_DIR -Filter 'backup_*.log' | Where-Object {
    $_.LastWriteTime -lt $cutoff
} | ForEach-Object {
    Remove-Item $_.FullName -Force
}

# Remove stale BACKUP_FAILED marker if this backup succeeded
$failMarker = Join-Path $BACKUP_DIR 'BACKUP_FAILED'
if (Test-Path $failMarker) {
    Remove-Item $failMarker -Force
    Write-Host '[INFO] Removed stale BACKUP_FAILED marker (previous failure resolved).'
}

Write-Host "[$(Get-Date)] Cleanup complete. Deleted $deleted old dump(s)."
Write-Host '[SUCCESS] Backup job finished.'
