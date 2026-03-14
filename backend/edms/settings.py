# =============================================================================
# FILE: backend/edms/settings.py
# EDMS-LDO Django settings — LAN-first, no internet dependency
# =============================================================================
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ───────────────────────────────────────────────────────────────────────────
# Security
# ───────────────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'change-me-in-production-use-env-var')
DEBUG      = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,0.0.0.0').split(',')
# For LAN deployment add your server IP: e.g. '192.168.1.100'

# ───────────────────────────────────────────────────────────────────────────
# Application definition
# ───────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    # EDMS apps
    'master',           # Master data: LocomotiveType, ComponentCatalog, Lookups
    'config_mgmt',      # LocoConfig + ECN register
    'prototype',        # Prototype Inspection + Punch Items
    'ocr_queue',        # OCR Job queue
    'audit_log',        # System-wide audit trail
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # must be first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'edms.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'edms.wsgi.application'

# ───────────────────────────────────────────────────────────────────────────
# Database — PostgreSQL (primary), fallback to SQLite for quick dev
# ───────────────────────────────────────────────────────────────────────────
_DB_ENGINE = os.environ.get('DB_ENGINE', 'django.db.backends.postgresql')

if _DB_ENGINE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     os.environ.get('DB_NAME',     'edms_db'),
            'USER':     os.environ.get('DB_USER',     'edms_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'edms_pass'),
            'HOST':     os.environ.get('DB_HOST',     '127.0.0.1'),
            'PORT':     os.environ.get('DB_PORT',     '5432'),
            'CONN_MAX_AGE': 60,
        }
    }

# ───────────────────────────────────────────────────────────────────────────
# Authentication — JWT via SimpleJWT
# ───────────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':  True,
    'AUTH_HEADER_TYPES':      ('Bearer',),
}

# ───────────────────────────────────────────────────────────────────────────
# CORS — LAN-only (no wildcard in production)
# ───────────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173'
).split(',')
# For LAN: add http://192.168.1.100:5173 etc. via .env

# ───────────────────────────────────────────────────────────────────────────
# File uploads
# ───────────────────────────────────────────────────────────────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', str(BASE_DIR / 'media'))

STATIC_URL  = '/static/'
STATIC_ROOT = str(BASE_DIR / 'staticfiles')

# ───────────────────────────────────────────────────────────────────────────
# Localisation (Indian Railways)
# ───────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Kolkata'
USE_I18N      = True
USE_TZ        = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
