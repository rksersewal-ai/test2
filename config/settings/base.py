# =============================================================================
# FILE: config/settings/base.py
# BUG FIX: Added missing INSTALLED_APPS entries:
#   - 'config_mgmt'       → LocoConfig + ECN register (backend/config_mgmt)
#   - 'prototype'         → Prototype Inspection + Punch Items (backend/prototype)
#   - 'django_celery_beat'→ Referenced in CELERY_BEAT_SCHEDULER but was absent,
#                           causing ImportError on Celery beat startup
# =============================================================================
import os
from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='change-me-in-production')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'django_celery_beat',    # BUG FIX: was referenced in CELERY_BEAT_SCHEDULER but missing here
    # Internal apps (apps/ package)
    'apps.core',
    'apps.edms',
    'apps.workflow',
    'apps.ocr',
    'apps.audit',
    'apps.dashboard',
    'apps.metadata',         # RESTORED Feature
    'apps.versioning',       # RESTORED Feature
    'apps.notifications',
    'apps.ml_classifier',
    'apps.pdf_tools',
    'apps.sanity',
    'apps.sharelinks',
    'apps.webhooks',
    'apps.scanner',
    'apps.pl_master',
    'apps.work_ledger',
    'apps.sdr',
    # Backend standalone apps (backend/ package, sit on sys.path via manage.py)
    'config_mgmt',           # BUG FIX: LocoConfig + ECN — was missing, migrations would fail
    'prototype',             # BUG FIX: Prototype Inspection — was missing, migrations would fail
    'bom',                   # RESTORED Feature
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
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     config('DB_NAME',     default='edms_ldo'),
        'USER':     config('DB_USER',     default='edms_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST':     config('DB_HOST',     default='localhost'),
        'PORT':     config('DB_PORT',     default='5432'),
        'OPTIONS': {'options': '-c search_path=public'},
        'CONN_MAX_AGE': 60,
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
        'rest_framework_simplejwt.authentication.JWTAuthentication',
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
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.UserRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {'user': '500/hour'},
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM':         'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'UPDATE_LAST_LOGIN':  True,
}

FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800
ALLOWED_UPLOAD_EXTENSIONS   = ['.pdf', '.tif', '.tiff', '.jpg', '.jpeg', '.png']

OCR_TESSERACT_CMD  = config('TESSERACT_CMD', default=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
OCR_DEFAULT_LANG   = 'eng'
OCR_DPI            = 300
OCR_WATCH_FOLDER   = config('OCR_WATCH_FOLDER', default=str(BASE_DIR / 'ocr_inbox'))
OCR_MAX_RETRIES    = 3

ALLOWED_IP_RANGES  = config('ALLOWED_IP_RANGES', default='192.168.0.0/16,10.0.0.0/8').split(',')

CELERY_BROKER_URL        = config('CELERY_BROKER_URL',    default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND    = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT    = ['json']
CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE          = 'Asia/Kolkata'
CELERY_BEAT_SCHEDULER    = 'django_celery_beat.schedulers:DatabaseScheduler'
