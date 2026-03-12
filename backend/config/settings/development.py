"""
PLW EDMS — Development Settings
"""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

CORS_ALLOW_ALL_ORIGINS = True

INSTALLED_APPS += ['django_extensions']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Show SQL in console (disable in large datasets)
# LOGGING['loggers']['django.db.backends'] = {
#     'handlers': ['console'], 'level': 'DEBUG', 'propagate': False,
# }
