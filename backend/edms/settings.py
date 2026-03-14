# =============================================================================
# FILE: backend/edms/settings.py
# HARDENED — performance + crash-proof
#
# Changes from previous version:
#  1. DB connection pool — CONN_MAX_AGE 60 -> 300 + CONN_HEALTH_CHECKS
#  2. DRF throttling — burst 60/min anonymous, 240/min authenticated
#  3. DRF exception handler — custom handler returns uniform JSON (no HTML 500)
#  4. Custom pagination — returns total_count + total_pages in every list
#  5. CONN_MAX_AGE extended for report/export endpoints (long queries)
#  6. Structured logging — all app errors captured to logs/edms.log
#  7. FILE_UPLOAD_MAX_MEMORY_SIZE — prevents crash on large PDF uploads
#  8. DATA_UPLOAD_MAX_MEMORY_SIZE — stops Django from rejecting form-data
# =============================================================================
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR  = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
SECRET_KEY    = os.environ.get('DJANGO_SECRET_KEY', 'change-me-in-production-use-env-var')
DEBUG         = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,0.0.0.0').split(',')

# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    # EDMS apps
    'master',
    'config_mgmt',
    'prototype',
    'ocr_queue',
    'audit_log',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF     = 'edms.urls'
WSGI_APPLICATION = 'edms.wsgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

# ---------------------------------------------------------------------------
# Database — PostgreSQL primary, SQLite fallback
# PERF: CONN_MAX_AGE=300 keeps connections alive for 5 min (was 60).
#       CONN_HEALTH_CHECKS=True discards stale connections silently.
# ---------------------------------------------------------------------------
_DB_ENGINE = os.environ.get('DB_ENGINE', 'django.db.backends.postgresql')
if _DB_ENGINE == 'sqlite':
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME'  : BASE_DIR / 'db.sqlite3',
    }}
else:
    DATABASES = {'default': {
        'ENGINE'            : 'django.db.backends.postgresql',
        'NAME'              : os.environ.get('DB_NAME',     'edms_db'),
        'USER'              : os.environ.get('DB_USER',     'edms_user'),
        'PASSWORD'          : os.environ.get('DB_PASSWORD', 'edms_pass'),
        'HOST'              : os.environ.get('DB_HOST',     '127.0.0.1'),
        'PORT'              : os.environ.get('DB_PORT',     '5432'),
        'CONN_MAX_AGE'      : 300,     # keep connection alive 5 min (perf)
        'CONN_HEALTH_CHECKS': True,    # auto-discard stale connections
        'OPTIONS'           : {'connect_timeout': 10},
    }}

# ---------------------------------------------------------------------------
# DRF — throttling + custom pagination + custom exception handler
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'edms.authentication.JWTCookieAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # PERF: Custom pagination adds total_count + total_pages to every list
    'DEFAULT_PAGINATION_CLASS': 'edms.pagination.EDMSPageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # STABILITY: Uniform JSON error body on every 4xx/5xx — no HTML 500 pages
    'EXCEPTION_HANDLER': 'edms.exceptions.edms_exception_handler',
    # STABILITY: Throttling prevents accidental DB overload on LAN
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/min',
        'user': '240/min',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME' : timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS' : True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES'     : ('Bearer',),
    'USER_ID_FIELD'         : 'id',
    'USER_ID_CLAIM'         : 'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'edms.auth.EDMSTokenObtainPairSerializer',
}

# ---------------------------------------------------------------------------
# CORS — LAN-only
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ORIGINS', 'http://localhost:4173,http://127.0.0.1:4173'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CORS_ORIGINS', 'http://localhost:4173,http://127.0.0.1:4173'
).split(',')

# ---------------------------------------------------------------------------
# File uploads — prevent crash on large PDF/drawing uploads
# ---------------------------------------------------------------------------
MEDIA_URL  = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', str(BASE_DIR / 'media'))
STATIC_URL  = '/static/'
STATIC_ROOT = str(BASE_DIR / 'staticfiles')

FILE_UPLOAD_MAX_MEMORY_SIZE  = 50 * 1024 * 1024   # 50 MB in-memory before spooling
DATA_UPLOAD_MAX_MEMORY_SIZE  = 50 * 1024 * 1024   # 50 MB for multipart form data
FILE_UPLOAD_TEMP_DIR         = str(BASE_DIR / 'media' / '_tmp')

# ---------------------------------------------------------------------------
# Localisation — Indian Railways (IST)
# ---------------------------------------------------------------------------
LANGUAGE_CODE      = 'en-us'
TIME_ZONE          = 'Asia/Kolkata'
USE_I18N           = True
USE_TZ             = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Structured logging — writes to logs/edms.log + console
# ---------------------------------------------------------------------------
LOGGING = {
    'version'                 : 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name} {process:d} {thread:d} — {message}',
            'style' : '{',
        },
        'simple': {
            'format': '{asctime} [{levelname}] {name} — {message}',
            'style' : '{',
        },
    },
    'handlers': {
        'console': {
            'class'    : 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class'      : 'logging.handlers.RotatingFileHandler',
            'filename'   : str(LOG_DIR / 'edms.log'),
            'maxBytes'   : 10 * 1024 * 1024,  # 10 MB per file
            'backupCount': 5,
            'formatter'  : 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level'   : 'WARNING',
    },
    'loggers': {
        'django'         : {'handlers': ['console', 'file'], 'level': 'WARNING', 'propagate': False},
        'django.request' : {'handlers': ['console', 'file'], 'level': 'ERROR',   'propagate': False},
        'edms'           : {'handlers': ['console', 'file'], 'level': 'DEBUG' if DEBUG else 'INFO', 'propagate': False},
    },
}
