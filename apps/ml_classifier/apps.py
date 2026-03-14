from django.apps import AppConfig


class MlClassifierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'apps.ml_classifier'
    verbose_name       = 'ML Metadata Classifier'
