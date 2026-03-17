# PLW EDMS — LAN Deployment Guide
## Stack: Nginx + Waitress + NSSM on Windows

This is the **complete, step-by-step** guide to deploy PLW EDMS on a Windows server
for LAN-only access (Indian Railways office network).

---

## Prerequisites (install once)

| Tool | Download | Notes |
|---|---|---|
| Python 3.11+ | https://python.org | Add to PATH |
| PostgreSQL 15+ | https://postgresql.org | Install as Windows Service |
| Redis for Windows | https://github.com/microsoftarchive/redis/releases | Install as Windows Service |
| Node.js 18+ | https://nodejs.org | For frontend build |
| Nginx for Windows | https://nginx.org/en/download.html | Extract to `C:\nginx` |
| NSSM | https://nssm.cc/download | Extract `nssm.exe`, add to PATH |
| Git | https://git-scm.com | Includes OpenSSL |
| Tesseract OCR | https://github.com/UB-Mannheim/tesseract/wiki | For OCR features |

---

## First-Time Deployment

### Step 1 — Clone the repo
```bat
cd D:\
git clone https://github.com/rksersewal-ai/test2 plw_edms
cd plw_edms
```

### Step 2 — Create Python virtual environment
```bat
python -m venv venv
venv\Scripts\pip install --upgrade pip
venv\Scripts\pip install -r requirements.txt
venv\Scripts\pip install -r requirements-optional.txt
```

### Step 3 — Create `.env` file
```bat
copy .env.production.example .env
notepad .env
```
Fill in: `SECRET_KEY`, `DB_PASSWORD`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and your server IP.

Generate a strong SECRET_KEY with:
```bat
venv\Scripts\python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Step 4 — Create PostgreSQL database
```sql
-- Run in psql as postgres superuser:
CREATE USER edms_user WITH PASSWORD 'your-strong-password';
CREATE DATABASE edms_ldo OWNER edms_user;
GRANT ALL PRIVILEGES ON DATABASE edms_ldo TO edms_user;
```

### Step 5 — Generate SSL certificate
```bat
deployment\generate_ssl_cert.bat
```
To avoid browser warnings on office PCs, install `C:\nginx\ssl\edms.crt`
as a Trusted Root CA via `certmgr.msc → Trusted Root Certification Authorities → Import`.

### Step 6 — Build React frontend
```bat
deployment\build_frontend.bat
```

### Step 7 — Install Windows Services (run as Administrator)
```bat
deployment\install_services.bat
```

This installs and starts:
- **EDMS-Backend** — Waitress WSGI server on `127.0.0.1:8765`
- **EDMS-Nginx** — Nginx reverse proxy on ports 80/443

### Step 8 — Create superuser
```bat
set DJANGO_SETTINGS_MODULE=config.settings.production
venv\Scripts\python manage.py createsuperuser
```

### Step 9 — Access the app
- App: `https://192.168.1.100` (or `https://edms.lan` if DNS configured)
- Admin: `https://192.168.1.100/admin/`

---

## Updating After Code Changes

Every time you push new code to GitHub, just run on the server:
```bat
deployment\update_edms.bat
```
This does: `git pull` → `pip install` → migrations → collectstatic → service restart.

If frontend code changed, also run:
```bat
deployment\build_frontend.bat
```

---

## Service Management

```bat
# Check service status
nssm status EDMS-Backend
nssm status EDMS-Nginx

# Restart manually
nssm restart EDMS-Backend
nssm restart EDMS-Nginx

# View logs
type D:\plw_edms\logs\waitress_stderr.log
type C:\nginx\logs\nginx_error.log

# Reload nginx config (zero-downtime)
C:\nginx\nginx.exe -s reload

# Test nginx config syntax
C:\nginx\nginx.exe -t
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Login fails / 401 errors | Wrong `CORS_ALLOWED_ORIGINS` or `CSRF_TRUSTED_ORIGINS` | Update `.env` to match exact URL users access |
| 403 Forbidden | `LanOnlyMiddleware` blocking request | Add client IP range to `ALLOWED_IP_RANGES` in `.env` |
| Static files missing (404 on CSS/JS) | `collectstatic` not run | Run `update_edms.bat` or `manage.py collectstatic` |
| Port 8000 refused | DSC Signer occupying port 8000 | Use `WAITRESS_PORT=8765` (already set in template) |
| SSL cert warning | Self-signed cert not trusted | Install cert in `certmgr.msc` as Trusted Root CA |
| Redis connection error | Redis service not running | `net start Redis` or start from Services panel |
| DB connection error | PostgreSQL service not running | `net start postgresql-x64-15` |
| Celery tasks not running | Celery worker not started | Run: `venv\Scripts\celery -A celery_app worker -l info` |

---

## Directory Structure on Server

```
D:\plw_edms\          ← project root (git clone)
├── .env              ← production env vars (never commit)
├── venv\             ← Python virtual environment
├── logs\             ← waitress logs
├── media\            ← uploaded documents
├── staticfiles\      ← collectstatic output
└── frontend\dist\    ← built React app (or C:\EDMS\frontend\dist)

C:\nginx\             ← Nginx installation
├── conf\nginx.conf   ← copied from deployment\nginx_windows.conf
└── ssl\              ← edms.crt, edms.key
```
