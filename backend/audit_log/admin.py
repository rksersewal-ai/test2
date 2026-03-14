from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display   = ['id', 'timestamp', 'user', 'action', 'model', 'object_repr', 'ip_address']
    list_filter    = ['action', 'model']
    search_fields  = ['user__username', 'object_repr', 'description']
    ordering       = ['-timestamp']
    readonly_fields = ['timestamp', 'user', 'action', 'model', 'object_id',
                       'object_repr', 'changes', 'ip_address', 'description']

    def has_add_permission(self, request):
        return False  # audit logs are system-generated only

    def has_change_permission(self, request, obj=None):
        return False  # immutable
