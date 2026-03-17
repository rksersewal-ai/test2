# PLW EDMS — Security & Deployment Checklist

## Pre-Production (must complete before go-live)

### Environment / Secrets
- [ ] Copy `.env.example` to `.env` and fill all values — never commit `.env`
- [ ] Set `SECRET_KEY` to a 50+ char random string (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] Set `DJANGO_SETTINGS_MODULE=config.settings.production`
- [ ] Set `ALLOWED_HOSTS` to your LAN IPs and hostname(s) e.g. `192.168.1.100,plw-edms.local`
- [ ] Set `ALLOWED_IP_RANGES` to your actual office subnets e.g. `192.168.1.0/24`
- [ ] Set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` with a dedicated PostgreSQL user
- [ ] Set `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`
- [ ] Rotate all default passwords before first user login

### HTTPS / TLS
- [ ] Obtain or generate a self-signed TLS certificate for `plw-edms.local`
- [ ] Configure nginx (or IIS ARR) as HTTPS reverse proxy on port 443
- [ ] Set `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`
- [ ] Set `SECURE_HSTS_SECONDS=31536000`, `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`, `SECURE_HSTS_PRELOAD=True`
- [ ] Bind Gunicorn / Waitress to `127.0.0.1` only — never expose Django directly on LAN port

### Database
- [ ] Create a dedicated DB user with `CONNECT`, `SELECT`, `INSERT`, `UPDATE`, `DELETE` only (no `DROP`, `CREATE`)
- [ ] Enable PostgreSQL SSL connections
- [ ] Schedule daily `pg_dump` backup to a separate path
- [ ] Verify `pg_dump` restore works in staging before go-live
- [ ] Confirm `trg_audit_log_immutable` trigger is present: `SELECT tgname FROM pg_trigger WHERE tgname = 'trg_audit_log_immutable';`

### Application
- [ ] Run `python manage.py migrate` with all migrations applied
- [ ] Run `python manage.py check --deploy --settings=config.settings.production`
- [ ] Run `python manage.py collectstatic`
- [ ] Load seed data: `python manage.py loaddata fixtures/work_types.json`
- [ ] Create at least one `ADMIN` role user via `python manage.py createsuperuser`
- [ ] Verify `LANOnlyMiddleware` is active (try accessing from outside subnet — expect 403)
- [ ] Verify `AuditMiddleware` writes to `audit_log` on POST requests
- [ ] Verify immutable trigger: `UPDATE audit_log SET success=false WHERE id=1;` must raise exception

### File Storage
- [ ] Set `MEDIA_ROOT` to a path outside the web root
- [ ] Ensure the Windows service account has write permission to `MEDIA_ROOT` only
- [ ] Configure IIS to deny direct access to `MEDIA_ROOT` path
- [ ] Consider enabling Windows BitLocker on the data volume

### OCR Worker
- [ ] Tesseract 5.x installed and `tesseract` binary in system PATH
- [ ] `pdf2image` and `poppler` installed and tested
- [ ] Schedule `python manage.py run_ocr_worker --loop --interval 30` via Windows Task Scheduler
- [ ] Set Task Scheduler to restart on failure
- [ ] Confirm OCR worker and Waitress logs are written under `logs\`

## Post-Deployment Verification
- [ ] Login page loads at `https://plw-edms.local`
- [ ] Dashboard shows correct document/work ledger counts
- [ ] Upload a test PDF and verify OCR queue item is created
- [ ] Wait 30–60s and verify OCR result appears
- [ ] Create a Work Ledger entry and confirm audit log entry is written
- [ ] Verify Audit Log page shows all recent actions
- [ ] Test that a `VIEWER` role user cannot POST to `/api/v1/edms/documents/`

## Maintenance
- [ ] Monthly: review `audit_log` for anomalies
- [ ] Quarterly: rotate JWT `SECRET_KEY` (requires all users to re-login)
- [ ] Annually: review and update `ALLOWED_IP_RANGES` if office network changes
- [ ] Keep Tesseract and Python dependencies updated on isolated schedule (test before applying)
