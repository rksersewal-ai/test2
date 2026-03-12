# EDMS — Electronic Document Management System
## PLW EDMS + LDO Work Ledger

**Version:** 1.0.0  
**Organization:** Production Unit — Locomotive Workshop  
**Deployment:** Local-first, LAN-only, Windows Server  
**Stack:** Python 3.11 · Django 4.2 · DRF · PostgreSQL 15 · React · Tesseract OCR  

---

## Overview

PLW EDMS is an integrated **Electronic Document Management System** and **LDO Work Ledger** platform designed for Indian Railways engineering offices. It centralizes engineering documents, preserves full revision history, enables OCR-based search of scanned drawings, and records LDO work activities in a neutral, audit-safe manner.

## Key Features

- 📄 Document & Revision Management with full lifecycle tracking
- 🔍 OCR Pipeline (Tesseract 5.x) for scanned PDF/image indexing
- 📋 LDO Work Ledger — factual record-keeping, not approval automation
- 🔒 JWT Auth + RBAC with immutable audit logs
- 🏢 Local-first, offline-capable, no cloud dependency
- 🔗 eOffice file number referencing (metadata only)

## Project Structure

```
EDMS-LDO/
├── backend/          # Django application
│   ├── apps/         # Modular Django apps
│   ├── config/       # Settings (base/dev/prod)
│   ├── middleware/   # Security + Audit middleware
│   ├── sql/          # Database migration scripts
│   ├── scripts/      # Worker and utility scripts
│   └── utils/        # Shared utilities
├── frontend/         # React SPA
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── store/
│   └── public/
└── docs/             # Documentation
```

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Tesseract OCR 5.x
- Node.js 18+ (for frontend)

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # Configure your .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Database Schema

```bash
cd backend/sql
psql -U edms_user -d plw_edms -f 001_initial_schema.sql
psql -U edms_user -d plw_edms -f 002_audit_tables.sql
psql -U edms_user -d plw_edms -f 003_ocr_tables.sql
psql -U edms_user -d plw_edms -f 004_indexes.sql
psql -U edms_user -d plw_edms -f 005_functions.sql
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## License

Internal use only — Production Unit, Locomotive Workshop.
