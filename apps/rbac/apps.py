from django.apps import AppConfig


class RbacConfig(AppConfig):
    name = 'apps.rbac'
    verbose_name = 'RBAC (Fine-Grained — Future)'
    # No models. No migrations. Intentional stub.
    # See README.md for rationale.
