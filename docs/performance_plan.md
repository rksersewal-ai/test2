# PLW EDMS — Performance Optimisation Plan

## Problem Statement

During peak hours (morning 9–11 AM, afternoon 3–5 PM) multiple engineers
browse the document list, run searches, and upload revisions simultaneously.
Without caching or connection pooling, every request hits PostgreSQL fresh,
causing latency spikes and server saturation.

---

## What Was Already Good (Before This PR)

| Area | Status |
|------|--------|
| N+1 on document list | Fixed (FIX #6: prefetch cache in `_latest_revision`) |
| Runaway search queries | Fixed (statement_timeout in repository.py) |
| SHA-256 off request thread | Fixed (FIX #8: async Celery task) |
| Bulk update table lock | Fixed (FIX #16: MAX_BULK_IDS=500) |
| File atomic upload | Fixed (FIX #15: transaction.atomic + disk cleanup) |

---

## Layer 1 — Database (Committed)

### 1.1 Persistent Connections (`CONN_MAX_AGE=60`)
Each Waitress worker thread reuses the same PostgreSQL connection for 60 seconds
instead of connecting on every request. Saves **10–30 ms per request** on a LAN.

### 1.2 Global Safety Net (`statement_timeout=30s`)
Set at the PostgreSQL connection level via `OPTIONS`. Any query running longer
than 30 seconds is cancelled. Search endpoints set their own LOCAL timeouts
(3s autocomplete, 8s unified) which take precedence.

### 1.3 PostgreSQL Indexes Already In Place
```sql
-- These already exist from previous migrations:
CREATE INDEX ON edms_document (document_number);      -- B-tree, exact match
CREATE INDEX ON edms_document (eoffice_file_number);   -- B-tree
CREATE INDEX USING GIN ON ocr_ocrresult               -- GIN tsvector, OCR text
    (to_tsvector('english', full_text));
-- pg_trgm trigram index used by similarity search
```

### 1.4 Recommended PostgreSQL.conf Tuning (manual, DBA action)
Edit `postgresql.conf` on the PostgreSQL server:
```ini
# Memory (adjust to 25% of server RAM)
shared_buffers          = 512MB    # was probably 128MB default
effective_cache_size    = 1536MB   # estimate of OS + PG cache
work_mem                = 16MB     # per sort/hash operation
maintenance_work_mem    = 128MB    # for VACUUM, index rebuilds

# Connections
max_connections         = 50       # 16 Waitress threads + Celery workers + headroom

# Checkpoints (reduce I/O spikes)
checkpoint_completion_target = 0.9
wal_buffers              = 16MB

# Autovacuum (keep tables healthy)
autovacuum_vacuum_scale_factor  = 0.05
autovacuum_analyze_scale_factor = 0.02
```

---

## Layer 2 — Application Caching (Committed)

### 2.1 FileBasedCache (zero setup, Windows-native)
- Location: `<project_root>/cache_store/`
- Default TTL: 5 minutes for list pages, 1 hour for dropdowns
- Survives Waitress restarts (unlike LocMemCache)
- Upgrade path: swap to Redis by editing 3 lines in `config/settings/cache.py`

### 2.2 Cache Invalidation on Writes
Every write operation (create, update, status change, approve, reject,
bulk update, new revision) calls `invalidate_document_cache()` which
busts the affected cached pages. Users always see fresh data after a write.

### 2.3 Cache Key Strategy
```
edms:<ViewClassName>:<user_id>:<sorted_query_params>
```
Per-user caching means User A's filtered view doesn't pollute User B's.

### 2.4 Dropdown Caching (Categories, Document Types)
These change rarely. Cache with `CACHE_LONG = 3600s` (1 hour).
Call `invalidate_dropdown_cache()` from admin when you add a new category.

---

## Layer 3 — Web Server (Committed)

### 3.1 Waitress Tuning (`config/waitress_config.py`)
```
threads=16         → 16 simultaneous requests without queuing
channel_timeout=120 → large PDF uploads don't get cut off
max_request_body_size=100MB → matches Django's FILE_UPLOAD_MAX_MEMORY_SIZE
connection_limit=200 → handles browser parallelism from 50 users
cleanup_interval=30 → releases idle TCP sockets faster
```

### 3.2 Whitenoise Static Files
All JS/CSS/images are served with `Cache-Control: max-age=31536000, immutable`
(1 year). The browser downloads each asset only once per deploy, not once
per page load. This alone reduces server requests by 60–80% on repeat visits.

---

## Layer 4 — Frontend (To Implement)

These are code changes in the React frontend (not committed yet — do separately):

### 4.1 HTTP Cache-Control Headers (Quick Win)
Add to API calls that return list data:
```ts
// In your axios/fetch interceptor:
response.headers['Cache-Control'] = 'private, max-age=60';
```
The browser caches the list response for 60 seconds. Back-button navigation
is instant — no API call at all.

### 4.2 React Query / SWR for Stale-While-Revalidate
Wrap all `useEffect + fetch` patterns with React Query:
```tsx
import { useQuery } from '@tanstack/react-query';

const { data, isLoading } = useQuery({
  queryKey: ['documents', filters],
  queryFn:  () => fetchDocuments(filters),
  staleTime: 60_000,   // show cached data for 60s before refetching
});
```
This eliminates loading spinners on repeat visits to the same page.

### 4.3 Virtualised List Rendering
If the document list has > 200 rows, switch to `react-window` or `react-virtual`:
```tsx
import { FixedSizeList } from 'react-window';
```
Renders only the visible rows, not all 500. Eliminates browser jank on scroll.

### 4.4 Lazy Load PDF Viewer
The PDF viewer (heavy bundle) should only load when a document is clicked:
```tsx
const PDFViewer = React.lazy(() => import('./PDFViewer'));
```

---

## Layer 5 — PostgreSQL Maintenance (Manual, Weekly)

Run these on the PostgreSQL server weekly (can schedule via pgAgent or Task Scheduler):
```sql
-- Rebuild bloated indexes (especially after bulk imports)
REINDEX TABLE edms_document;
REINDEX TABLE edms_file_attachment;
REINDEX TABLE ocr_ocrresult;

-- Refresh statistics for query planner
ANALYZE edms_document;
ANALYZE edms_file_attachment;
ANALYZE ocr_ocrresult;

-- Check for slow queries (run ad-hoc when peak slowness reported)
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

---

## Expected Impact Summary

| Optimisation | Estimated Saving |
|--------------|------------------|
| CONN_MAX_AGE=60 | 10–30ms per request |
| FileBasedCache on list pages | 80–90% of list requests served from cache |
| Whitenoise immutable assets | 60–80% fewer static file requests |
| Waitress 16 threads | Handles 16 concurrent users without queuing |
| statement_timeout=30s global | Prevents any single runaway query hanging a thread |
| pg_trgm + GIN indexes | Search < 100ms instead of 2–5s |
| React Query stale-while-revalidate | Zero loading spinners on repeat navigation |

---

## Upgrade Path to Redis (When Needed)

If the user base grows beyond 50 concurrent users, upgrade to Redis:
1. Install Redis on Windows: `winget install Redis.Redis`
2. `pip install django-redis redis`
3. Edit `config/settings/cache.py`: uncomment Option B, comment out Option A
4. Restart Waitress — no code changes needed

The `apps/core/cache.py` helpers (`cache_get`, `cache_set`, `cache_delete_pattern`)
already support both backends transparently.
