from django.contrib import admin
from .models import UserRole, DocumentPermissionOverride


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display  = ['user', 'role', 'section', 'document_type', 'is_active', 'granted_at', 'expires_at']
    list_filter   = ['role', 'is_active']
    search_fields = ['user__username']
    raw_id_fields = ['user', 'granted_by']


@admin.register(DocumentPermissionOverride)
class DocumentPermissionOverrideAdmin(admin.ModelAdmin):
    list_display  = ['user', 'document', 'permission', 'override', 'created_at', 'expires_at']
    list_filter   = ['permission', 'override']
    search_fields = ['user__username', 'document__document_number']
