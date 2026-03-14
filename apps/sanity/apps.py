from django.apps import AppConfig


class SanityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'apps.sanity'
    verbose_name       = 'Document Sanity Checker'
