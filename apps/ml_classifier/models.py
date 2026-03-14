# =============================================================================
# FILE: apps/ml_classifier/models.py
# SPRINT 5 — ML Classifier
#
# Stores trained model artefacts + per-document prediction audit trail.
# Models are serialised as joblib files saved under MEDIA_ROOT/ml_models/.
# The DB row just tracks version, accuracy, and training metadata.
# =============================================================================
from django.db import models
from django.conf import settings


class ClassifierModel(models.Model):
    """
    One trained version of a classifier.
    target: what it predicts  (document_type | category | correspondent)
    """
    class Target(models.TextChoices):
        DOCUMENT_TYPE  = 'document_type',  'Document Type'
        CATEGORY       = 'category',       'Category'
        CORRESPONDENT  = 'correspondent',  'Correspondent'

    target          = models.CharField(max_length=30, choices=Target.choices, db_index=True)
    version         = models.PositiveIntegerField(default=1)
    model_path      = models.CharField(
        max_length=500,
        help_text='Path relative to MEDIA_ROOT, e.g. ml_models/doc_type_v3.joblib'
    )
    label_path      = models.CharField(
        max_length=500,
        help_text='Path to LabelEncoder joblib file'
    )
    accuracy        = models.FloatField(null=True, blank=True,
                          help_text='Test-set accuracy from last training run (0–1)')
    training_docs   = models.IntegerField(null=True, blank=True,
                          help_text='Number of documents used for training')
    is_active       = models.BooleanField(default=True,
                          help_text='Only one active model per target is used for inference')
    trained_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='trained_models'
    )
    trained_at      = models.DateTimeField(auto_now_add=True)
    notes           = models.TextField(blank=True)

    class Meta:
        db_table        = 'ml_classifier_model'
        unique_together = [('target', 'version')]
        ordering        = ['target', '-version']

    def __str__(self):
        return f'[{self.target}] v{self.version} acc={self.accuracy:.2%}' if self.accuracy else \
               f'[{self.target}] v{self.version}'


class ClassificationResult(models.Model):
    """
    Audit trail: one row per document per classifier run.
    Stores top-3 predictions with confidence scores.
    User can accept or override the suggestion.
    """
    class Outcome(models.TextChoices):
        PENDING   = 'PENDING',   'Pending user review'
        ACCEPTED  = 'ACCEPTED',  'Accepted'
        OVERRIDDEN = 'OVERRIDDEN', 'Overridden by user'
        REJECTED  = 'REJECTED',  'Rejected'

    document        = models.ForeignKey(
        'edms.Document', on_delete=models.CASCADE,
        related_name='classification_results'
    )
    classifier      = models.ForeignKey(
        ClassifierModel, on_delete=models.SET_NULL,
        null=True, related_name='results'
    )
    target          = models.CharField(max_length=30)
    # JSON list of [{label, label_id, confidence}], up to 3 items
    predictions     = models.JSONField(default=list)
    top_label       = models.CharField(max_length=200, blank=True)
    top_label_id    = models.IntegerField(null=True, blank=True)
    top_confidence  = models.FloatField(null=True, blank=True)
    outcome         = models.CharField(
        max_length=15, choices=Outcome.choices, default=Outcome.PENDING
    )
    reviewed_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='classification_reviews'
    )
    reviewed_at     = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ml_classification_result'
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['document', 'target']),
            models.Index(fields=['outcome']),
        ]

    def __str__(self):
        return (
            f'{self.document.document_number} '
            f'[{self.target}] → {self.top_label} ({self.top_confidence:.0%})'
        ) if self.top_confidence else f'{self.document.document_number} [{self.target}]'
