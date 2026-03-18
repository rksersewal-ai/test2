# =============================================================================
# FILE: config/settings/cache.py
#
# Caching configuration for PLW EDMS LAN deployment.
#
# Strategy:
#   Development  : LocMemCache (zero setup, process-local)
#   Production   : FileBasedCache (zero setup, LAN-safe, survives restarts)
#   Optional     : Redis (uncomment section below when Redis is available)
#
# FileBasedCache is deliberately chosen over Redis as the default because:
#   - Zero extra services to install on Windows Server
#   - Survives Waitress/IIS app pool recycles (unlike LocMemCache)
#   - Adequate for a LAN deployment with < 50 concurrent users
#   - Easy to clear: just delete the cache directory
# =============================================================================
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Option A: FileBasedCache (DEFAULT — zero extra setup on Windows Server)
# ---------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': str(BASE_DIR / 'cache_store'),
        'TIMEOUT': 300,           # 5 minutes default TTL
        'OPTIONS': {
            'MAX_ENTRIES': 5000,  # ~5000 cached responses max, then LRU eviction
        },
    }
}

# ---------------------------------------------------------------------------
# Option B: Redis (uncomment when Redis is installed on the LAN server)
# Requires: pip install django-redis redis
# ---------------------------------------------------------------------------
# REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/1')
# CACHES = {
#     'default': {
#         'BACKEND':  'django_redis.cache.RedisCache',
#         'LOCATION': REDIS_URL,
#         'OPTIONS': {
#             'CLIENT_CLASS':          'django_redis.client.DefaultClient',
#             'SOCKET_CONNECT_TIMEOUT': 2,
#             'SOCKET_TIMEOUT':        2,
#             'IGNORE_EXCEPTIONS':     True,   # degrade to no-cache on Redis failure
#             'MAX_CONNECTIONS':       50,
#         },
#         'TIMEOUT': 300,
#         'KEY_PREFIX': 'edms',
#     }
# }

# ---------------------------------------------------------------------------
# Session backend: use cache for speed (file cache is persistent enough for LAN)
# ---------------------------------------------------------------------------
SESSION_ENGINE         = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS    = 'default'

# Cache-Control headers sent with DRF responses
# (complements per-view @cache_control decorators)
CACHE_MIDDLEWARE_SECONDS = 0   # Never cache at middleware level — controlled per-view
