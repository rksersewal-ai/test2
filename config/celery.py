# =============================================================================
# FILE: config/celery.py
# =============================================================================
import os
import sys
from pathlib import Path
from celery import Celery

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / 'backend'

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(1, str(BACKEND_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('edms_ldo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# No beat schedule is registered here until the referenced periodic tasks exist
# in the active app stack. The previous schedule pointed at task names that were
# not discoverable anywhere in this project.
app.conf.beat_schedule = {}
