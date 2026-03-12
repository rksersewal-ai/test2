from django.contrib import admin
from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'username', 'module', 'action',
        'entity_type', 'entity_identifier', 'success', 'ip_address',
    ]
    list_filter  = ['module', 'action', 'success']
    search_fields = ['username', 'description', 'entity_identifier']
    readonly_fields = [f.name for f in AuditLog._meta.get_fields()]
    ordering = ['-timestamp']

    def has_add_permission(self, request):    return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
