# =============================================================================
# FILE: apps/ml_classifier/inference.py
# SPRINT 5 — Inference service
#
# Loads active models from disk (cached in-process after first call).
# Provides classify_document(doc) → dict of predictions per target.
# Thread-safe for Django's multi-threaded WSGI (models are read-only after load).
# =============================================================================
import logging
import threading
from pathlib import Path
from typing  import Optional

from django.conf import settings
from apps.ml_classifier.runtime import ensure_ml_dependencies

log     = logging.getLogger('ml_classifier')
_lock   = threading.Lock()
_cache: dict = {}   # target → {'pipe': Pipeline, 'le': LabelEncoder, 'version': int}

ML_DIR = Path(settings.MEDIA_ROOT) / 'ml_models'


def _load_model(target: str, force: bool = False) -> Optional[dict]:
    """Load (or reload) the active model for a target. Returns None if not trained yet."""
    ensure_ml_dependencies()

    import joblib
    from apps.ml_classifier.models import ClassifierModel
    with _lock:
        cm = ClassifierModel.objects.filter(target=target, is_active=True).first()
        if not cm:
            return None
        cached = _cache.get(target)
        if cached and cached['version'] == cm.version and not force:
            return cached
        # Load from disk
        pipe = joblib.load(Path(settings.MEDIA_ROOT) / cm.model_path)
        le   = joblib.load(Path(settings.MEDIA_ROOT) / cm.label_path)
        entry = {'pipe': pipe, 'le': le, 'version': cm.version, 'cm': cm}
        _cache[target] = entry
        log.info(f'[ML] Loaded {target} v{cm.version} into cache')
        return entry


def reload_all():
    """Force reload all cached models — call after retraining."""
    for t in ('document_type', 'category', 'correspondent'):
        _load_model(t, force=True)


def predict_one(target: str, text: str, top_n: int = 3) -> list:
    """
    Return top_n predictions for a single text string.
    Each item: {label, label_id (int index), confidence (float 0-1)}
    Returns [] if no model is available.
    """
    ensure_ml_dependencies()

    import numpy as np
    entry = _load_model(target)
    if not entry:
        return []

    pipe = entry['pipe']
    le   = entry['le']

    try:
        proba = pipe.predict_proba([text])[0]
    except Exception as e:
        log.warning(f'[ML] predict_proba failed for {target}: {e}')
        return []

    top_idx = np.argsort(proba)[::-1][:top_n]
    return [
        {
            'label':      str(le.classes_[i]),
            'label_id':   int(i),
            'confidence': float(round(proba[i], 4)),
        }
        for i in top_idx
        if proba[i] > 0.01   # skip near-zero probability classes
    ]


def classify_document(doc) -> dict:
    """
    Run all active classifiers against a Document ORM instance.
    Returns:
    {
      'document_type': [{label, label_id, confidence}, ...],
      'category':      [...],
      'correspondent': [...],
    }
    """
    from apps.ml_classifier.pipeline import _build_text
    text = _build_text(doc)
    if not text.strip():
        return {'document_type': [], 'category': [], 'correspondent': []}

    return {
        'document_type': predict_one('document_type', text),
        'category':      predict_one('category',      text),
        'correspondent': predict_one('correspondent', text),
    }


def classify_and_save(document_id: int) -> dict:
    """
    Full inference cycle:
    1. Load Document from DB.
    2. Run classifiers.
    3. Persist ClassificationResult rows.
    4. Return predictions dict.
    """
    ensure_ml_dependencies()

    from apps.edms.models import Document
    from apps.ml_classifier.models import ClassificationResult

    try:
        doc = Document.objects.select_related(
            'document_type', 'category'
        ).prefetch_related(
            'revisions__files', 'correspondent_links__correspondent'
        ).get(pk=document_id)
    except Document.DoesNotExist:
        log.error(f'[ML] classify_and_save: Document #{document_id} not found')
        return {}

    predictions = classify_document(doc)

    for target, preds in predictions.items():
        if not preds:
            continue
        top = preds[0]
        cm  = _cache.get(target, {}).get('cm')

        # Upsert: one result per document per target (update if re-classified)
        ClassificationResult.objects.update_or_create(
            document=doc,
            target=target,
            defaults=dict(
                classifier      = cm,
                predictions     = preds,
                top_label       = top['label'],
                top_label_id    = top['label_id'],
                top_confidence  = top['confidence'],
                outcome         = ClassificationResult.Outcome.PENDING,
                reviewed_by     = None,
                reviewed_at     = None,
            )
        )

    return predictions
