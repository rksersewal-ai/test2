from django.apps import AppConfig


class TotpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'apps.totp'
    verbose_name       = '2FA / TOTP'
