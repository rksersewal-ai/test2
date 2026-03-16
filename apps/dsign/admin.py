from django.contrib import admin
from .models import SigningCertificate, DocumentSignature


@admin.register(SigningCertificate)
class SigningCertificateAdmin(admin.ModelAdmin):
    list_display  = ['user', 'serial_number', 'issued_by', 'valid_from', 'valid_until', 'status']
    list_filter   = ['status']
    search_fields = ['user__username', 'serial_number', 'issued_by']
    readonly_fields = ['created_at']


@admin.register(DocumentSignature)
class DocumentSignatureAdmin(admin.ModelAdmin):
    list_display  = ['document', 'signed_by', 'role', 'status', 'it_act_compliant', 'signed_at']
    list_filter   = ['role', 'status', 'it_act_compliant']
    search_fields = ['document__document_number', 'signed_by__username']
    readonly_fields = ['signature_hash', 'file_checksum', 'signed_at']
