from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.core.models import User, Section


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'is_active']
    search_fields = ['code', 'name']
    list_filter = ['is_active']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'full_name', 'employee_code', 'section', 'role', 'is_active']
    search_fields = ['username', 'full_name', 'employee_code']
    list_filter = ['role', 'section', 'is_active']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal', {'fields': ('full_name', 'email', 'employee_code', 'designation')}),
        ('Organization', {'fields': ('section', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'full_name', 'employee_code', 'section', 'role', 'password1', 'password2')}),
    )
