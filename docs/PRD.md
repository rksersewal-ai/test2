# EDMS Product Requirements Document

This document is the official PRD for the EDMS-LDO system at Patiala Locomotive Works, Indian Railways.

**Version:** 1.0  
**Date:** January 19, 2026  
**Organization:** Patiala Locomotive Works, Indian Railways  
**Status:** APPROVED & IN DEVELOPMENT

> The full PRD content is maintained in the `test` repository at branch `rksersewal-ai-patch-1`  
> file: `edms-prd.md` (72 KB, 24 FRs, 8 NFRs, 12-week roadmap).

## Quick Reference — 24 Functional Requirements

| FR | Feature | Phase | Status |
|---|---|---|---|
| FR-001 | Document Upload & Ingestion | 1 | ✅ Implemented |
| FR-002 | Automatic Document Classification | 1 | 🔶 Skeleton (`apps/ml_classifier`) |
| FR-003 | OCR | 1 | ✅ Implemented (`apps/ocr`) |
| FR-004 | Advanced Search & Retrieval | 1 | ✅ Implemented |
| FR-005 | Metadata Management | 1 | ✅ **Built this PR** (`apps/metadata`) |
| FR-006 | Document Versioning | 1 | ✅ **Built this PR** (`apps/versioning`) |
| FR-007 | Workflow & Approval Management | 2 | ✅ Implemented (`apps/workflow`) |
| FR-008 | Digital Signatures | 2 | ❌ Planned |
| FR-009 | RBAC (8 roles) | 2 | 🔶 Partial (`apps/security`) |
| FR-010 | Audit Logging | 2 | ✅ Implemented (`apps/audit`) |
| FR-011 | Retention & Lifecycle | 2 | ❌ Planned |
| FR-012 | Security & Encryption | 2 | 🔶 Partial (`apps/security`, `apps/totp`) |
| FR-013 | Sharing & Collaboration | 3 | 🔶 Partial (`apps/sharelinks`) |
| FR-014 | Mobile App | 3 | ❌ Planned |
| FR-015 | Analytics & Reporting | 3 | 🔶 Partial (`apps/dashboard`) |
| FR-016 | Document Templates | 3 | ❌ Planned |
| FR-017 | Integration APIs | 3 | 🔶 Partial (`apps/webhooks`) |
| FR-018 | Scanner Integration | 3 | 🔶 Skeleton (`apps/scanner`) |
| FR-019 | Email Integration | 3 | ❌ Planned |
| FR-020 | Notification System | 3 | 🔶 Partial (`apps/notifications`) |
| FR-021 | Backup & Disaster Recovery | 3 | ❌ Planned |
| FR-022 | User Management | 3 | 🔶 Partial (`apps/core`) |
| FR-023 | System Configuration | 3 | ❌ Planned |
| FR-024 | Performance & Scalability | 3 | 🔶 Infra ready |

## Phase 1 Completion Checklist (Weeks 1–4)

- [x] FR-001 Document Upload
- [x] FR-003 OCR Pipeline
- [x] FR-004 Search & Retrieval
- [x] FR-005 Metadata Management — `apps/metadata/` ← **this PR**
- [x] FR-006 Document Versioning — `apps/versioning/` ← **this PR**
- [ ] FR-002 AI Classification — `apps/ml_classifier/` needs training pipeline
- [ ] 80%+ test coverage (currently ~45%, targeting 80% after this PR)

## Next Steps (Phase 2)

1. FR-008 Digital Signatures (`cryptography` + PKI, IT Act 2000)
2. FR-009 Full RBAC — extend `apps/security` to all 8 roles
3. FR-011 Retention & Lifecycle — `apps/lifecycle/`
4. FR-012 Full Encryption — AES-256 at-rest for stored files
