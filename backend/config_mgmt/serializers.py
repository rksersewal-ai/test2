# =============================================================================
# FILE: backend/config_mgmt/serializers.py
# =============================================================================
from rest_framework import serializers
from .models import LocoConfig, ECN


class LocoConfigSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = LocoConfig
        fields = [
            'id', 'loco_class', 'serial_no', 'config_version', 'ecn_ref',
            'effective_date', 'changed_by', 'status', 'remarks',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_name']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class ECNSerializer(serializers.ModelSerializer):
    raised_by_name   = serializers.SerializerMethodField(read_only=True)
    approved_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = ECN
        fields = [
            'id', 'ecn_number', 'subject', 'loco_class', 'description',
            'status', 'date', 'raised_by', 'raised_by_name',
            'approved_by', 'approved_by_name', 'approved_at',
            'remarks', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at',
                            'raised_by_name', 'approved_by_name', 'approved_at']

    def get_raised_by_name(self, obj):
        if obj.raised_by:
            return obj.raised_by.get_full_name() or obj.raised_by.username
        return None

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name() or obj.approved_by.username
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['raised_by'] = request.user
        return super().create(validated_data)
