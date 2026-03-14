from django.apps import AppConfig


class WorkLedgerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.work_ledger'
    verbose_name = 'Work Ledger'

    def ready(self):
        import apps.work_ledger.signals  # noqa: F401
