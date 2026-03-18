# Instant Search — Everything-Style (PLW EDMS)

## Overview

The `apps.search` module provides two production-ready search endpoints that together
deliver an **Everything by Voidtools–style** instant search experience within the EDMS
LAN application — **no internet, no external search engine, no new infrastructure**.

---

## Endpoints

### 1. Typeahead Autocomplete
```
GET /api/v1/search/autocomplete/?q=WAG9&limit=10
```
- Returns up to 10 lightweight suggestions as the user types (call after every 250 ms debounce)
- Searches: `document_number`, `title`, `keywords`, `file_name`
- Backed by existing pg_trgm trigram index
- Hard statement_timeout: **3 seconds** (HTTP 503 on timeout, not 500)

### 2. Unified Full Search
```
GET /api/v1/search/unified/?q=WAG9+drawing&page=1&page_size=25
```
- Cross-entity ranked search across 5 sources
- Backed by GIN tsvector index (OCR text) + icontains (metadata)
- Hard statement_timeout: **8 seconds**
- Results ranked by match source priority (doc_number > title > filename > ocr > note > correspondent)

---

## Search Sources & Priority

| Rank | Source | Fields Searched | Index Used |
|------|--------|----------------|------------|
| 5.0 | Document number | `document_number` | B-tree (`db_index=True`) |
| 4.0 | Document title | `title` | pg_trgm trigram |
| 3.0 | Keywords | `keywords` | pg_trgm trigram |
| 2.5 | eOffice fields | `eoffice_file_number`, `eoffice_subject`, `description` | icontains |
| 2.0 | File attachment | `file_name` | icontains |
| 1.5 | OCR text | `full_text` | **GIN tsvector** (migration 0003) |
| 1.0 | Document notes | `note_text` | icontains |
| 0.8 | Correspondent | `name`, `short_code` | icontains |

---

## Production Safety

| Risk | Mitigation |
|------|------------|
| Long-running query hangs DB connection | `SET LOCAL statement_timeout` (3s autocomplete, 8s unified) |
| Missing pg_trgm extension | Caught as `SearchUnavailableError` → HTTP 503, not 500 |
| SQL injection via user input | All values passed as parameterised `%s` — never interpolated |
| Single-char full-table scan | Minimum 2-char query enforced at view layer |
| Frontend hammering API on every keystroke | 250 ms debounce + AbortController in `useInstantSearch.ts` |
| Race-condition stale results | AbortController cancels previous request before new one fires |
| Huge result sets exhausting RAM | LIMIT/OFFSET enforced; hard ceiling 200 rows |

---

## No Migration Required

`apps.search` has **zero models** — no new DB tables, no migration to run.
It reads from existing tables using existing indexes.

---

## Frontend Integration

```tsx
import { useInstantSearch, useUnifiedSearch } from '@/hooks/useInstantSearch';

// In your global search bar component:
const { suggestions, loading } = useInstantSearch(inputValue);

// When user presses Enter:
const { results, count, pages } = useUnifiedSearch(submittedQuery, currentPage);
```

---

## File Preview on Result Click

Each result includes `id` (document ID). Wire the click handler to:
```
GET /api/v1/edms/documents/{id}/file/
```
This streams the file inline — the browser's native PDF viewer opens it directly.
