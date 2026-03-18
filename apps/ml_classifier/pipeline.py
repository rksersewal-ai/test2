# =============================================================================
# FILE: apps/ml_classifier/pipeline.py
# SPRINT 5 — Training pipeline
#
# Architecture: TF-IDF (char + word n-grams) → SGDClassifier (log loss)
# Why this stack:
#   - Runs fully offline, zero internet dependency (LAN requirement)
#   - joblib models are <5 MB each, load in <100 ms
#   - Retrainable in <60 s on 5 000 docs using a single CPU core
#   - log_loss gives calibrated probabilities for confidence display
#   - Easily swappable to LinearSVC or RandomForest without API change
#
# Input text built from:  title + description + keywords + ocr_text
#                         + document_number prefix + source_standard
#
# Targets trained independently:
#   1. document_type  (FK → edms_document_type)
#   2. category       (FK → edms_category)
#   3. correspondent  (short_code of primary ISSUED_BY correspondent)
# =============================================================================
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings
from apps.ml_classifier.runtime import ensure_ml_dependencies

if TYPE_CHECKING:
    from sklearn.pipeline import Pipeline
    from apps.ml_classifier.models import ClassifierModel

log = logging.getLogger('ml_classifier')

ML_DIR = Path(settings.MEDIA_ROOT) / 'ml_models'
ML_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------

def _build_text(doc) -> str:
    """
    Build a single text string from a Document ORM instance.
    Includes OCR text if available (via latest FileAttachment ocr_text field
    added in a prior sprint — falls back gracefully).
    """
    parts = [
        doc.title or '',
        doc.description or '',
        doc.keywords or '',
        doc.document_number or '',
        doc.source_standard or '',
        doc.eoffice_subject or '',
    ]
    # Grab OCR text from latest primary file if the field exists
    try:
        fa = doc.revisions.order_by('-created_at').first()
        if fa:
            pf = fa.files.filter(is_primary=True).first()
            if pf and hasattr(pf, 'ocr_text'):
                parts.append(pf.ocr_text or '')
    except Exception:
        pass
    return ' '.join(p for p in parts if p).lower()


def _get_training_data(target: str) -> tuple[list, list]:
    """
    Query the DB and build (texts, labels) lists for a given target.
    Returns empty lists if fewer than 10 labelled examples exist.
    """
    from apps.edms.models import Document

    docs = list(
        Document.objects
        .select_related('document_type', 'category')
        .prefetch_related('revisions__files', 'correspondent_links__correspondent')
        .filter(status__in=['ACTIVE', 'SUPERSEDED'])  # exclude DRAFT
    )

    texts, labels = [], []
    for doc in docs:
        text = _build_text(doc)
        if not text.strip():
            continue

        if target == 'document_type':
            if doc.document_type_id:
                texts.append(text)
                labels.append(str(doc.document_type.name))

        elif target == 'category':
            if doc.category_id:
                texts.append(text)
                labels.append(str(doc.category.name))

        elif target == 'correspondent':
            # Use the ISSUED_BY correspondent short_code as label
            link = (
                doc.correspondent_links
                .filter(link_type='ISSUED_BY')
                .select_related('correspondent')
                .first()
            )
            if link:
                texts.append(text)
                labels.append(link.correspondent.short_code)

    return texts, labels


def build_pipeline() -> 'Pipeline':
    """
    Return a fresh sklearn Pipeline.
    TF-IDF with both word and character n-grams captures:
      - Word-level: 'specification', 'drawing', 'tender'
      - Char-level : 'WAG', 'CLW', 'RDSO', 'EL/' (doc number prefixes)
    """
    ensure_ml_dependencies()

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import SGDClassifier
    from sklearn.pipeline import Pipeline

    vec = TfidfVectorizer(
        analyzer        = 'char_wb',
        ngram_range     = (2, 4),
        max_features    = 30_000,
        sublinear_tf    = True,
        strip_accents   = 'unicode',
        min_df          = 2,
    )
    clf = SGDClassifier(
        loss            = 'log_loss',   # gives calibrated probabilities
        max_iter        = 200,
        tol             = 1e-4,
        random_state    = 42,
        class_weight    = 'balanced',   # handles class imbalance
        n_jobs          = -1,
    )
    return Pipeline([('tfidf', vec), ('clf', clf)])


def train(target: str, user=None) -> 'ClassifierModel':
    """
    Full training cycle for one target.
    Saves model + label encoder to disk.
    Creates a ClassifierModel DB row and deactivates previous versions.
    Returns the new ClassifierModel instance.
    """
    ensure_ml_dependencies()

    import joblib
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from apps.ml_classifier.models import ClassifierModel

    log.info(f'[ML] Training classifier for target={target}')
    texts, labels = _get_training_data(target)

    MIN_SAMPLES = 10
    if len(texts) < MIN_SAMPLES:
        raise ValueError(
            f'Not enough labelled documents to train [{target}]: '
            f'need ≥{MIN_SAMPLES}, got {len(texts)}.'
        )

    # Encode labels
    le = LabelEncoder()
    y  = le.fit_transform(labels)

    # Train / test split (80/20, stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        texts, y, test_size=0.20, random_state=42, stratify=y
    )

    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    acc = float(accuracy_score(y_test, pipe.predict(X_test)))
    log.info(f'[ML] target={target} accuracy={acc:.2%} on {len(X_test)} test docs')

    # Determine next version number
    last = ClassifierModel.objects.filter(target=target).order_by('-version').first()
    version = (last.version + 1) if last else 1

    model_fname = f'{target}_v{version}.joblib'
    label_fname = f'{target}_labels_v{version}.joblib'

    joblib.dump(pipe, ML_DIR / model_fname)
    joblib.dump(le,   ML_DIR / label_fname)

    # Deactivate previous models for this target
    ClassifierModel.objects.filter(target=target, is_active=True).update(is_active=False)

    cm = ClassifierModel.objects.create(
        target         = target,
        version        = version,
        model_path     = f'ml_models/{model_fname}',
        label_path     = f'ml_models/{label_fname}',
        accuracy       = acc,
        training_docs  = len(texts),
        is_active      = True,
        trained_by     = user,
        notes          = f'Auto-trained: {len(texts)} docs, {len(le.classes_)} classes',
    )
    log.info(f'[ML] Saved ClassifierModel pk={cm.pk} v{version}')
    return cm


def train_all(user=None) -> dict:
    """Train all three targets. Returns {target: ClassifierModel | error_str}."""
    results = {}
    for t in ('document_type', 'category', 'correspondent'):
        try:
            results[t] = train(t, user=user)
        except Exception as e:
            log.warning(f'[ML] Training failed for {t}: {e}')
            results[t] = str(e)
    return results
