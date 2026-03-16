from rest_framework import serializers
from .models import SigningCertificate, DocumentSignature


class SigningCertificateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model  = SigningCertificate
        fields = ['id', 'user', 'username', 'serial_number', 'issued_by',
                  'valid_from', 'valid_until', 'status', 'created_at']
        read_only_fields = ['id', 'username', 'created_at']


class DocumentSignatureSerializer(serializers.ModelSerializer):
    signed_by_username = serializers.CharField(source='signed_by.username', read_only=True)
    document_number    = serializers.CharField(source='document.document_number', read_only=True)

    class Meta:
        model  = DocumentSignature
        fields = [
            'id', 'document', 'document_number', 'version', 'signed_by',
            'signed_by_username', 'certificate', 'role', 'signature_hash',
            'file_checksum', 'status', 'remarks', 'signed_at', 'it_act_compliant',
        ]
        read_only_fields = ['id', 'signature_hash', 'file_checksum',
                            'signed_at', 'signed_by_username', 'document_number']
