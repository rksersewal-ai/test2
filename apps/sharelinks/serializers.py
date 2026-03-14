# =============================================================================
# FILE: apps/sharelinks/serializers.py
# SPRINT 7
# =============================================================================
from rest_framework import serializers
from apps.sharelinks.models import ShareLink
from django.conf import settings


class ShareLinkSerializer(serializers.ModelSerializer):
    created_by_name  = serializers.CharField(source='created_by.get_full_name', read_only=True)
    document_number  = serializers.CharField(source='document.document_number', read_only=True)
    is_valid         = serializers.BooleanField(read_only=True)
    public_url       = serializers.SerializerMethodField()
    has_password     = serializers.SerializerMethodField()

    def get_public_url(self, obj):
        request = self.context.get('request')
        base    = request.build_absolute_uri('/') if request else 'http://localhost/'
        return f'{base.rstrip("/")}/s/{obj.token}/'

    def get_has_password(self, obj):
        return bool(obj.password_hash)

    class Meta:
        model  = ShareLink
        fields = [
            'id', 'token', 'public_url',
            'document', 'document_number', 'revision',
            'access_level', 'label', 'has_password',
            'expires_at', 'is_active', 'is_valid',
            'max_uses', 'use_count', 'rate_limit_per_hour',
            'created_by', 'created_by_name', 'created_at',
            'revoked_at',
        ]
        read_only_fields = [
            'token', 'use_count', 'created_by', 'created_at', 'revoked_at',
        ]


class CreateShareLinkSerializer(serializers.Serializer):
    document_id       = serializers.IntegerField()
    revision_id       = serializers.IntegerField(required=False, allow_null=True)
    access_level      = serializers.ChoiceField(
        choices=ShareLink.AccessLevel.choices,
        default=ShareLink.AccessLevel.VIEW_FILE
    )
    label             = serializers.CharField(default='', allow_blank=True)
    expires_in_days   = serializers.IntegerField(default=7, min_value=1, max_value=365)
    max_uses          = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    rate_limit_per_hour = serializers.IntegerField(default=20, min_value=1)
    password          = serializers.CharField(
        required=False, allow_blank=True, write_only=True,
        help_text='Optional link password. Stored as bcrypt hash.'
    )


class PublicDocumentSerializer(serializers.Serializer):
    """Read-only shape of what the public view returns."""
    document_number = serializers.CharField()
    title           = serializers.CharField()
    description     = serializers.CharField()
    category        = serializers.CharField(allow_null=True)
    document_type   = serializers.CharField(allow_null=True)
    status          = serializers.CharField()
    revision_number = serializers.CharField(allow_null=True)
    revision_date   = serializers.CharField(allow_null=True)
    access_level    = serializers.CharField()
    expires_at      = serializers.CharField()
    can_download    = serializers.BooleanField()


class VerifyPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
