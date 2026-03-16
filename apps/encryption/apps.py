from django.apps import AppConfig

class EncryptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.encryption'
    verbose_name = 'AES-256 File Encryption'
