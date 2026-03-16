from django.contrib import admin
from .models import EncryptedBlob


@admin.register(EncryptedBlob)
class EncryptedBlobAdmin(admin.ModelAdmin):
    list_display  = ['attachment', 'key_hint', 'encrypted_at']
    readonly_fields = ['encrypted_data', 'iv', 'encrypted_at']
    search_fields = ['attachment__file_name']
