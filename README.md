# PLW EDMS + LDO Work Ledger

**Engineering Document Management System + LDO Work Activity Recording Platform**
Built for Indian Railways Production Unit | Local-first, LAN-only deployment

---

## Architecture

```
React (Frontend) <-> Django REST Framework (Backend) <-> PostgreSQL 15
                              |
                    OCR Pipeline (Tesseract)
                    LAN-only Middleware
                    Immutable Audit Log
```

## Tech Stack
- **Backend:** Python 3.11 / Django 4.2 / DRF 3.15
- **Database:** PostgreSQL 15
- **OCR:** Tesseract + PyMuPDF + Pillow
- **Auth:** JWT (djangorestframework-simplejwt)
- **Deployment:** Windows LAN / IIS or gunicorn + nginx

## Project Structure

```
EDMS-LDO/
├── apps/
│   ├── core/          # Users, Sections, RBAC
│   ├── edms/          # Documents, Revisions, File Attachments
│   ├── workflow/      # LDO Work Ledger, Work Types, Vendors, Tenders
│   ├── ocr/           # OCR Queue, Results, Entity Extraction
│   ├── audit/         # Immutable Audit Log
│   └── dashboard/     # Stats endpoints
├── config/
│   ├── settings/      # base, development, production
│   └── urls.py        # Root URL config
├── middleware/        # AuditMiddleware, LanOnlyMiddleware
├── sql/               # PostgreSQL schema and index scripts
├── scripts/           # Seed and management scripts
├── docs/              # Gap analysis and architecture docs
├── manage.py
├── requirements.txt
└── .env.example
```

## Quick Start

```bash
# 1. Clone and setup virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 2. Configure environment
copy .env.example .env
# Edit .env with your DB credentials

# 3. Setup PostgreSQL
psql -U postgres -c "CREATE DATABASE edms_ldo;"
psql -U postgres -c "CREATE USER edms_user WITH PASSWORD 'your-password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE edms_ldo TO edms_user;"
psql -d edms_ldo -f sql/001_create_extensions.sql

# 4. Run Django migrations
python manage.py makemigrations
python manage.py migrate

# 5. Seed master data
python manage.py shell < scripts/seed_master_data.py

# 6. Run development server
python manage.py runserver
```

## API Endpoints

| Module | Base URL | Methods |
|---|---|---|
| Auth | `/api/v1/auth/token/` | POST |
| Users | `/api/v1/core/users/` | GET, POST, PATCH |
| Sections | `/api/v1/core/sections/` | GET, POST |
| Documents | `/api/v1/edms/documents/` | GET, POST, PATCH, DELETE |
| Revisions | `/api/v1/edms/revisions/` | GET, POST, PATCH |
| Work Ledger | `/api/v1/workflow/work-ledger/` | GET, POST, PATCH |
| Tenders | `/api/v1/workflow/tenders/` | GET, POST |
| OCR Queue | `/api/v1/ocr/queue/` | GET, POST |
| OCR Results | `/api/v1/ocr/results/` | GET |
| Audit Logs | `/api/v1/audit/logs/` | GET |
| Dashboard | `/api/v1/dashboard/stats/` | GET |

## Security
- JWT authentication, 8-hour access tokens
- RBAC: ADMIN, SECTION_HEAD, ENGINEER, LDO_STAFF, AUDIT, VIEWER
- LAN-only middleware blocks requests from outside `ALLOWED_IP_RANGES`
- Immutable audit log (model-level + PostgreSQL rule-level protection)
- File upload limited to `.pdf`, `.tif`, `.tiff`, `.jpg`, `.jpeg`, `.png`

## Gap Analysis
See [docs/GAP_ANALYSIS.md](docs/GAP_ANALYSIS.md) for full gap matrix and remaining work.

---
*PLW — Patiala Locomotive Works | Indian Railways*
