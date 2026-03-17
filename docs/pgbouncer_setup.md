# pgBouncer Setup Guide — PLW EDMS (Windows LAN Deployment)

> **Fix #20 — DB Connection Pool Exhaustion**
> Waitress uses a synchronous thread-per-request model. Without pgBouncer,
> each thread holds its own PostgreSQL connection open. Under moderate load
> (20+ concurrent users) this exhausts PostgreSQL's `max_connections` (default 100).
> pgBouncer in **transaction pooling** mode reduces this to a fixed small pool.

---

## 1. Install pgBouncer on Windows

```powershell
# Option A: via Chocolatey (recommended)
choco install pgbouncer -y

# Option B: download MSI from https://www.pgbouncer.org/install.html
# and install to C:\pgBouncer\
```

---

## 2. Configure `pgbouncer.ini`

Create `C:\pgBouncer\pgbouncer.ini`:

```ini
[databases]
; Route edms_ldo traffic to local PostgreSQL on port 5432
edms_ldo = host=127.0.0.1 port=5432 dbname=edms_ldo

[pgbouncer]
listen_addr       = 127.0.0.1
listen_port       = 6432
auth_type         = md5
auth_file         = C:\pgBouncer\userlist.txt

; TRANSACTION pooling is required for Django (session pooling breaks ORM)
pool_mode         = transaction

; Keep a small server-side pool — tune based on your PostgreSQL max_connections
default_pool_size = 20
max_client_conn   = 200
reserve_pool_size = 5
reserve_pool_timeout = 3

log_connections   = 0
log_disconnections = 0
log_pooler_errors  = 1
server_idle_timeout = 600
```

---

## 3. Create `userlist.txt`

```powershell
# Generate MD5 hash: md5(password + username)
# Python one-liner:
python -c "import hashlib; u='edms_user'; p='YOUR_DB_PASSWORD'; print('\"' + u + '\" \"md5' + hashlib.md5((p+u).encode()).hexdigest() + '\"')"

# Paste output into C:\pgBouncer\userlist.txt, e.g.:
# "edms_user" "md5abc123..."
```

---

## 4. Install & Start pgBouncer as a Windows Service

```powershell
# Install service
"C:\pgBouncer\bin\pgbouncer.exe" -service install "C:\pgBouncer\pgbouncer.ini"

# Start service
Start-Service pgbouncer

# Verify it's listening on port 6432
netstat -an | findstr 6432
```

---

## 5. Update `.env` to point Django at pgBouncer

```env
# Before:
DB_HOST=localhost
DB_PORT=5432

# After: route Django through pgBouncer proxy
DB_HOST=127.0.0.1
DB_PORT=6432

# IMPORTANT: with transaction pooling, persistent connections are harmful.
# Keep CONN_MAX_AGE=0 (already set as default in base.py)
DB_CONN_MAX_AGE=0
```

---

## 6. Verify Connection

```powershell
# Test Django can connect via pgBouncer
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('OK')"

# Check pgBouncer pool stats
psql -h 127.0.0.1 -p 6432 -U edms_user pgbouncer -c "SHOW POOLS;"
```

---

## 7. PostgreSQL `max_connections` Tuning

With pgBouncer, you can safely lower `max_connections` in `postgresql.conf`:

```conf
# postgresql.conf  (C:\Program Files\PostgreSQL\16\data\postgresql.conf)
max_connections = 50      # pgBouncer handles the multiplexing
shared_buffers  = 256MB   # 25% of RAM is a good starting point
```

Restart PostgreSQL after changing `max_connections`:
```powershell
Restart-Service postgresql-x64-16
```

---

## Expected Outcome

| Metric | Without pgBouncer | With pgBouncer |
|--------|-------------------|----------------|
| PostgreSQL connections under 20 users | 20–40 | 5–8 |
| `max_connections` headroom | Low | High |
| Connection creation overhead | Per request | Pooled |
| Risk of `too many connections` error | High | Eliminated |
