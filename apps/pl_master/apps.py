from django.apps import AppConfig


class PlMasterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pl_master'
    verbose_name = 'PL Master'

    def ready(self):
        import apps.pl_master.signals  # noqa: F401 — register DrawingMaster/SpecMaster alteration signals
