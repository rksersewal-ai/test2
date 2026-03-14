# =============================================================================
# INSTRUCTION: Add these 4 lines to INSTALLED_APPS in your settings.py
# Then run: python manage.py makemigrations && python manage.py migrate
# =============================================================================
"""
INSTALLED_APPS = [
    ...existing apps...
    'config_mgmt',   # LocoConfig + ECN register
    'prototype',     # Prototype Inspection + Punch Items
    'ocr_queue',     # OCR Job queue
    'audit_log',     # System-wide audit trail
]
"""

# =============================================================================
# INSTRUCTION: Add these 4 includes to your main urls.py urlpatterns
# =============================================================================
"""
from django.urls import path, include

urlpatterns = [
    ...existing patterns...
    path('api/config/',    include('config_mgmt.urls')),
    path('api/prototype/', include('prototype.urls')),
    path('api/ocr/',       include('ocr_queue.urls')),
    path('api/audit/',     include('audit_log.urls')),
]
"""
