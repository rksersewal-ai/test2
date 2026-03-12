"""Security settings fragment — imported by base.py / production.py.

Usage in base.py:
    from config.settings.security import *   # noqa: F403

All values can be overridden via environment variables.
"""
import os

# ---- Session & Cookie hardening ----
SESSION_COOKIE_HTTPONLY  = True
SESSION_COOKIE_SAMESITE  = 'Strict'
SESSION_COOKIE_AGE       = 28800          # 8 hours — one work shift
CSRF_COOKIE_HTTPONLY     = True
CSRF_COOKIE_SAMESITE     = 'Strict'
SECURE_BROWSER_XSS_FILTER = True

# In production (behind nginx/IIS with HTTPS) set these to True:
SESSION_COOKIE_SECURE    = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE       = os.getenv('CSRF_COOKIE_SECURE',    'False') == 'True'
SECURE_SSL_REDIRECT      = os.getenv('SECURE_SSL_REDIRECT',   'False') == 'True'
SECURE_HSTS_SECONDS      = int(os.getenv('HSTS_SECONDS', '0'))   # enable after HTTPS confirmed

# ---- JWT (SimpleJWT) ----
from datetime import timedelta  # noqa: E402
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':   timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME':  timedelta(days=1),
    'ROTATE_REFRESH_TOKENS':   True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN':       True,
    'ALGORITHM':               'HS256',
    'AUTH_HEADER_TYPES':       ('Bearer',),
    'USER_ID_FIELD':           'id',
    'USER_ID_CLAIM':           'user_id',
}

# ---- Password validation ----
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---- LAN network restrictions ----
# Set to your actual office subnet(s)
ALLOWED_LAN_NETWORKS = os.getenv(
    'ALLOWED_LAN_NETWORKS',
    '192.168.0.0/16,10.0.0.0/8,127.0.0.0/8'
).split(',')

# ---- DRF throttling (basic DoS protection on LAN) ----
REST_FRAMEWORK_THROTTLE = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '600/minute',
    },
}

# ---- File upload limits ----
DATA_UPLOAD_MAX_MEMORY_SIZE = 52_428_800    # 50 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52_428_800

# ---- ALLOWED_HOSTS (LAN deployment) ----
# Override completely via env var  DJANGO_ALLOWED_HOSTS=192.168.1.100,plw-edms.local
_extra_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = ['localhost', '127.0.0.1'] + [h.strip() for h in _extra_hosts.split(',') if h.strip()]
