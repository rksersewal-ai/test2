# PLW EDMS + LDO — Gap Analysis Report
**Date:** 2026-03-12 | **Status:** Week 1 Complete

## Executive Summary

| Area | Before Seeding | After This Batch | Priority |
|---|---|---|---|
| Repository | Only README.md | Full Django project structure | P0 ✅ |
| Figma Design | EDMS file present, 0 components published | Screens exist as design reference | P1 📋 |
| Config / Settings | MISSING | base, dev, prod settings seeded | P0 ✅ |
| Core (User/Section/RBAC) | MISSING | Models, serializers, views, URLs seeded | P0 ✅ |
| EDMS (Document/Revision/File) | MISSING | Models, serializers, views, URLs seeded | P0 ✅ |
| Workflow / LDO Work Ledger | MISSING | Models, serializers, views, URLs seeded | P0 ✅ |
| OCR Pipeline | MISSING | Models + Tesseract service seeded | P0 ✅ |
| Audit Log | MISSING | Immutable models + views seeded | P0 ✅ |
| Dashboard Stats | MISSING | Stats endpoint seeded | P1 ✅ |
| SQL Migrations | MISSING | 001–006 SQL files seeded | P0 ✅ |
| Security Middleware | MISSING | Audit + LAN-only middleware seeded | P0 ✅ |
| Frontend (React hooks) | Not started | Pending — Week 9 | P1 🔜 |
| Tests | Not started | Pending — Week 11 | P1 🔜 |
| Deployment config (nginx) | Not started | Pending — Week 12 | P1 🔜 |

## Remaining Gaps (Next Sprints)

### P0 — Release Blocking
- [ ] `apps/ocr/views.py` + `urls.py` — OCR queue API wiring
- [ ] `apps/ocr/serializers.py` — OCR serializers
- [ ] Django `migrations/` folders for each app
- [ ] `scripts/seed_master_data.py` — WorkType, Section, DocumentType master data

### P1 — Important
- [ ] React frontend hooks for EDMS, workflow, OCR
- [ ] `nginx.conf` for LAN reverse proxy
- [ ] `pytest` test suite (schema, endpoint, permission, OCR)
- [ ] `.env` production secrets documentation

### P2 — Enhancement
- [ ] Watermark / download-control extension points
- [ ] Advanced dashboard charts (docs by month, work closed trend)
- [ ] Figma component library sync with React components

## Architecture Conformance Notes
- System remains record-keeping oriented — no approval automation introduced.
- eOffice references stored as plain text fields only — not wired as workflow engine.
- All services are LAN-first, no external network calls in any module.
- Audit log enforced immutable at both model level and PostgreSQL rule level.
