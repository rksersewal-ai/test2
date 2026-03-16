# EDMS-LDO PRD Feature Status

**Source PRD:** PLW LDO Digital Management System v1.0 (amended, 05-Jan-2026, 101KB)
**Repo:** rksersewal-ai/EDMS-LDO  
**Last Updated:** 2026-03-16

---

## Phase 1 Status (Weeks 1–4) — Core Document Management

| FR | Feature | App | Status |
|---|---|---|---|
| FR-001 | Document Upload & Ingestion | `apps/edms/` | ✅ Done |
| FR-002 | AI Classification | `apps/ml_classifier/` | 🔶 Skeleton |
| FR-003 | OCR Pipeline | `apps/ocr/` | ✅ Done |
| FR-004 | Advanced Search & Retrieval | `apps/edms/filters.py` | ✅ Done |
| **FR-005** | **Metadata Management** | **`apps/metadata/`** | **✅ Built this PR** |
| **FR-006** | **Document Versioning + Alteration History** | **`apps/versioning/`** | **✅ Built this PR** |

## New DB Tables (this PR)

| Table | Model | Description |
|---|---|---|
| `meta_field` | `MetadataField` | Custom field definitions per DocumentType |
| `meta_document_value` | `DocumentMetadata` | Field values per document |
| `meta_history` | `MetadataHistory` | Immutable change audit trail |
| `ver_document_version` | `DocumentVersion` | Semantic file versions (v1.0, v1.1…) |
| `ver_alteration_history` | `AlterationHistory` | PRD Table 13.9 — full alteration record |
| `ver_version_annotation` | `VersionAnnotation` | User comments on versions |
| `ver_version_diff` | `VersionDiff` | Delta diff between versions |

## Post-Merge Steps

```bash
# 1. Add to INSTALLED_APPS in settings.py:
#    'apps.metadata',
#    'apps.versioning',

# 2. Add to root urls.py:
#    path('api/metadata/', include('apps.metadata.urls')),
#    path('api/versioning/', include('apps.versioning.urls')),

# 3. Migrations
python manage.py makemigrations metadata versioning
python manage.py migrate

# 4. Run Phase 1 tests
pytest tests/test_metadata.py tests/test_versioning.py tests/test_phase1_integration.py -v --cov=apps
```

## Phase 2 Next Steps

1. `FR-008` Digital Signatures — `apps/dsign/` (PKI, `cryptography` lib, IT Act 2000)
2. `FR-009` Full RBAC — extend `apps/security/` to all 7 roles defined in PRD 5.1.2
3. `FR-011` Retention & Lifecycle — `apps/lifecycle/`
4. `FR-012` AES-256 encryption at-rest for stored files
5. `FR-019` Email Integration — inbound email with attachment extraction
