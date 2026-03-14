# =============================================================================
# FILE: backend/master/serializers_pl_master.py
# SERIALIZER: PLMasterItemSerializer
# =============================================================================
from rest_framework import serializers
from .models_pl_master import PLMasterItem


class PLMasterItemSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    loco_types      = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )

    class Meta:
        model  = PLMasterItem
        fields = [
            'pl_number', 'description', 'uvam_id',
            'inspection_category', 'safety_item', 'loco_types',
            'application_area', 'used_in', 'is_active', 'remarks',
            'created_by_name', 'updated_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by_name', 'updated_by_name', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return ''

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return obj.updated_by.get_full_name() or obj.updated_by.username
        return ''
