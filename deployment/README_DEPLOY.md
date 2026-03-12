# PLW EDMS + LDO — Windows Deployment Guide

## Prerequisites

| Component | Version | Notes |
|---|---|---|
| Windows Server | 2019 / 2022 | Or Windows 10/11 for pilot |
| Python | 3.11.x | Add to PATH during install |
| PostgreSQL | 15.x | Install as Windows Service |
| Tesseract OCR | 5.x | Install from UB Mannheim builds |
| poppler | 24.x | Required by pdf2image; add bin/ to PATH |
| IIS | 10 | With ARR and URL Rewrite modules |
| Git | 2.x | For pulling updates |

## Step 1: Clone and Configure

```bat
git clone https://github.com/rksersewal-ai/EDMS-LDO.git D:\plw_edms
cd D:\plw_edms
copy .env.example .env
notepad .env
```

Fill `.env` completely before proceeding. Key values:
- `SECRET_KEY` — generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DATABASE_URL` — `postgresql://plw_edms_user:PASSWORD@localhost:5432/plw_edms_db`
- `DJANGO_ALLOWED_HOSTS` — `192.168.1.100,plw-edms.local`
- `ALLOWED_LAN_NETWORKS` — `192.168.1.0/24`
- `DEBUG` — `False`

## Step 2: Install Dependencies

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements-lock.txt
```

## Step 3: Setup Database

```sql
-- Run in psql as postgres superuser:
CREATE USER plw_edms_user WITH PASSWORD 'YOUR_STRONG_PASSWORD';
CREATE DATABASE plw_edms_db OWNER plw_edms_user;
GRANT ALL PRIVILEGES ON DATABASE plw_edms_db TO plw_edms_user;
```

## Step 4: Initialize Application

```bat
venv\Scripts\activate
python manage.py migrate
python manage.py loaddata fixtures/work_types.json
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## Step 5: Verify Immutable Trigger

```sql
-- Should return 1 row:
SELECT tgname FROM pg_trigger WHERE tgname = 'trg_audit_log_immutable';
-- Should raise exception:
UPDATE audit_log SET success=false WHERE id=1;
```

## Step 6: Configure Task Scheduler (OCR Worker)

```bat
schtasks /Create /XML deployment\task_scheduler_ocr_worker.xml /TN "PLW-EDMS-OCR-Worker"
```
Edit the XML first to set the correct `<UserId>` and paths.

## Step 7: Configure IIS

1. Install IIS + ARR + URL Rewrite modules (via Web Platform Installer)
2. Create new IIS Site pointing to `D:\plw_edms_site`
3. Copy `deployment\iis_web.config` to `D:\plw_edms_site\web.config`
4. Set Physical Path of `/static` virtual directory to `D:\plw_edms\staticfiles`
5. Set Physical Path of `/media` virtual directory to `D:\plw_edms\media`
6. Enable ARR proxy: IIS Manager → Application Request Routing → Server Proxy Settings → Enable proxy

## Step 8: Start

```bat
REM Run as Administrator:
deployment\start_edms.bat
```

## Step 9: Schedule Daily Backup

1. Edit `deployment\backup_db.bat` — set `PGPASSWORD` and paths
2. Task Scheduler → Create Basic Task → Daily 02:00 → `deployment\backup_db.bat`

## Running Tests

```bat
venv\Scripts\activate
pip install -r requirements-dev.txt
pytest tests/ -v --tb=short
pytest tests/ -v --cov=apps --cov-report=term-missing
```

## Updating (Zero-Downtime)

```bat
git pull origin main
venv\Scripts\activate
pip install -r requirements-lock.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
REM Restart app server:
taskkill /F /FI "WINDOWTITLE eq PLW-EDMS-App" /T
start "PLW-EDMS-App" C:\Python311\python.exe deployment\waitress_server.py
```
