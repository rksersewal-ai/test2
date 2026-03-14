# =============================================================================
# FILE: apps/ml_classifier/tasks.py
# SPRINT 5 — Celery tasks for ML Classifier
# =============================================================================
from celery import shared_task
import logging

log = logging.getLogger('ml_classifier')


@shared_task(name='ml.retrain_all', bind=True, max_retries=1)
def retrain_all_classifiers(self, user_id: int = None):
    """
    Full retrain of all classifiers.
    Triggered manually via admin UI or POST /api/ml/models/train/.
    Also scheduled weekly (see celery_app.py beat schedule update below).
    """
    try:
        user = None
        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(pk=user_id).first()

        from apps.ml_classifier.pipeline  import train_all
        from apps.ml_classifier.inference import reload_all

        results = train_all(user=user)
        reload_all()   # flush in-process cache so next request uses new models

        summary = {
            t: (f'v{m.version} acc={m.accuracy:.2%}' if hasattr(m, 'version') else str(m))
            for t, m in results.items()
        }
        log.info(f'[ML] retrain_all complete: {summary}')
        return summary

    except Exception as exc:
        log.error(f'[ML] retrain_all failed: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task(name='ml.classify_document')
def classify_document_task(document_id: int):
    """
    Classify a single document in the background.
    Triggered automatically from apps/edms/services.py after OCR completes.
    """
    from apps.ml_classifier.inference import classify_and_save
    result = classify_and_save(document_id)
    log.info(f'[ML] classify_document #{document_id}: {list(result.keys())}')
    return result
