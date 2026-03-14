# EDMS-LDO — Migration & Seed Setup Guide

> Run these commands **once** after cloning or pulling the branch for the first time.
> All commands assume you are in the project root directory.

---

## 1. Backend Setup

### 1.1 Create & activate virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
```

### 1.2 Install dependencies
```bash
pip install -r requirements.txt
```

### 1.3 Configure environment
Copy `.env.example` to `.env` and set:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://edms_user:password@localhost:5432/edms_db
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.0/24
```

### 1.4 Run migrations (creates ALL tables)
```bash
python manage.py migrate --settings=config.settings.development
```
Expected output: ~19 migration files applied across:
`core`, `edms`, `pl_master`, `sdr`, `work_ledger`, `scanner`, `audit`

### 1.5 Create superuser
```bash
python manage.py createsuperuser --settings=config.settings.development
```

---

## 2. Seed Data

### 2.1 Load Controlling Agencies (CLW/BLW/RDSO/ICF/PLW/ABB/SIEMENS/BHEL)
```bash
python manage.py seed_pl_master --settings=config.settings.development
```

### 2.2 Import Category Book from Excel
Place your Category Book Excel file as `data/category_book.xlsx`, then:
```bash
python manage.py import_category_book data/category_book.xlsx --settings=config.settings.development
# Dry run first (no DB writes):
python manage.py import_category_book data/category_book.xlsx --dry-run --settings=config.settings.development
# Skip rows with errors:
python manage.py import_category_book data/category_book.xlsx --skip-errors --settings=config.settings.development
```

### 2.3 Seed Work Categories
```bash
python manage.py shell --settings=config.settings.development -c "
from apps.work_ledger.models import WorkCategory
cats = ['Drawing Review','Specification Review','BOM Update','Correspondence',
        'Inspection','Testing','Meeting','Report Writing','RDSO Reference']
for c in cats:
    WorkCategory.objects.get_or_create(category_name=c, defaults={'is_active':True})
print('Work categories seeded.')
"
```

---

## 3. Start Backend Server
```bash
python manage.py runserver 0.0.0.0:8000 --settings=config.settings.development
```
Backend API available at: `http://<LAN-IP>:8000/api/v1/`

---

## 4. Start Frontend (Vite dev server)
```bash
cd frontend
npm install
npm run dev -- --host
```
Frontend available at: `http://<LAN-IP>:5173/`

---

## 5. Start Celery (optional — for SDR escalation & background tasks)
```bash
# In a separate terminal:
celery -A config worker -l info
celery -A config beat   -l info   # For scheduled SDR escalation
```

---

## 6. Quick Verify Checklist

| Check | Command | Expected |
|---|---|---|
| Migrations applied | `python manage.py showmigrations` | All ✔ |
| PL Master API | `curl http://localhost:8000/api/v1/pl-master/` | `{results:[...]}` |
| Work Ledger API | `curl http://localhost:8000/api/v1/work/entries/` | `{count:0,...}` |
| SDR API | `curl http://localhost:8000/api/v1/sdr/` | `{results:[...]}` |
| Admin panel | `http://localhost:8000/admin/` | Login page |
| Frontend login | `http://localhost:5173/login` | Login form |
