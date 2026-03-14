# =============================================================================
# FILE: backend/master/apps.py
# =============================================================================
from django.apps import AppConfig


class MasterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name  = 'master'
    label = 'master'

    def ready(self):
        """Ensure media/_tmp upload directory exists on startup."""
        import os
        from django.conf import settings
        tmp_dir = os.path.join(settings.MEDIA_ROOT, '_tmp')
        os.makedirs(tmp_dir, exist_ok=True)
