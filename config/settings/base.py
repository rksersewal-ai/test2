# =============================================================================
# FILE: config/settings/base.py
# CHANGES IN THIS COMMIT:
#   - Added 'search' throttle scope (120/min) — prevents search endpoint from
#     consuming the shared 'user' quota and blocking uploads/downloads.
#   - Added CELERY_TASK_ACKS_LATE, CELERY_TASK_REJECT_ON_WORKER_LOST,
#     CELERY_TASK_MAX_RETRIES — ensures OCR/checksum tasks are re-queued on
#     worker crash instead of silently lost.
#   - Removed 'apps.workledger' (duplicate dir, only 'apps.work_ledger' is
#     canonical). Added note about apps/dsign and apps/totp not being wired.
# =============================================================================
import os
import sys
from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR    = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = BASE_DIR / 'backend'

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(1, str(BACKEND_DIR))

SECRET_KEY = config('SECRET_KEY', default='change-me-in-production')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'django_celery_beat',
    'apps.core',
    'apps.edms',
    'apps.workflow',
    'apps.ocr',
    'apps.audit',
    'apps.dashboard',
    'apps.dsign',
    'apps.metadata',
    'apps.versioning',
    'apps.lifecycle',
    'apps.notifications',
    'apps.ml_classifier',
    'apps.pdf_tools',
    'apps.sanity',
    'apps.sharelinks',
    'apps.webhooks',
    'apps.scanner',
    'apps.pl_master',
    # apps.rbac — fine-grained object-level ACL stub (no models yet).
    # See apps/rbac/README.md. Canonical RBAC = apps.core.permissions.
    'apps.rbac',
    # apps.totp — 2FA via TOTP (NOT YET WIRED to URLs).
    # Enable when totp/urls.py is included in config/urls.py + frontend integrated.
    # 'apps.totp',
    'apps.work_ledger',   # canonical — apps/workledger/ dir is legacy residue, IGNORE
    'apps.sdr',
    'apps.search',
    'config_mgmt',
    'prototype',
    'bom',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.audit_middleware.AuditMiddleware',
    'middleware.security_middleware.LanOnlyMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     config('DB_NAME',     default='edms_ldo'),
        'USER':     config('DB_USER',     default='edms_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST':     config('DB_HOST',     default='localhost'),
        'PORT':     config('DB_PORT',     default='5432'),
        'OPTIONS':  {'options': '-c search_path=public'},
        'CONN_MAX_AGE': int(config('DB_CONN_MAX_AGE', default='0')),
    }
}

AUTH_USER_MODEL = 'core.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-in'
TIME_ZONE     = 'Asia/Kolkata'
USE_I18N      = True
USE_TZ        = True

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.core.authentication.JWTCookieAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon':        '60/minute',
        'user':        '600/minute',
        'ocr_submit':  config('OCR_SUBMIT_THROTTLE_RATE', default='20/hour'),
        'ocr_retry':   config('OCR_RETRY_THROTTLE_RATE',  default='10/hour'),
        # Dedicated search throttle — keeps search load off the shared 'user' bucket.
        # 120/min = 2 requests/second per user (autocomplete fires every 250ms but
        # client-side debounce reduces actual hits to ~4/s max, well within limit).
        'search':      config('SEARCH_THROTTLE_RATE', default='120/minute'),
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':    timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME':   timedelta(days=1),
    'ROTATE_REFRESH_TOKENS':    True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM':                'HS256',
    'AUTH_HEADER_TYPES':        ('Bearer',),
    'UPDATE_LAST_LOGIN':        True,
    'USER_ID_FIELD':            'id',
    'USER_ID_CLAIM':            'user_id',
}

FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800
ALLOWED_UPLOAD_EXTENSIONS   = ['.pdf', '.tif', '.tiff', '.jpg', '.jpeg', '.png']
OCR_MAX_FILE_MB             = int(config('OCR_MAX_FILE_MB', default='100'))

OCR_TESSERACT_CMD = config('TESSERACT_CMD',
                            default=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
OCR_DEFAULT_LANG  = 'eng'
OCR_DPI           = 300
OCR_WATCH_FOLDER  = config('OCR_WATCH_FOLDER', default=str(BASE_DIR / 'ocr_inbox'))
OCR_MAX_RETRIES   = 3

ALLOWED_IP_RANGES = config('ALLOWED_IP_RANGES',
                            default='192.168.0.0/16,10.0.0.0/8').split(',')

CELERY_BROKER_URL        = config('CELERY_BROKER_URL',     default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND    = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT    = ['json']
CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE          = 'Asia/Kolkata'
CELERY_BEAT_SCHEDULER    = 'django_celery_beat.schedulers:DatabaseScheduler'

# Task reliability: re-queue tasks on worker crash instead of silently losing them.
# ACKS_LATE=True means the message is only acknowledged AFTER the task completes.
# If the worker crashes mid-task (SIGKILL, OOM), the broker re-delivers it.
CELERY_TASK_ACKS_LATE              = True
CELERY_TASK_REJECT_ON_WORKER_LOST  = True
CELERY_TASK_MAX_RETRIES            = 3    # global default; tasks can override

CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_retries':            3,
    'interval_start':         0,
    'interval_step':          0.2,
    'interval_max':           0.5,
    'socket_timeout':         5,
    'socket_connect_timeout': 3,
}
CELERY_TASK_ALWAYS_EAGER                  = False
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
