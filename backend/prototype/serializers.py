# =============================================================================
# FILE: backend/prototype/serializers.py
# =============================================================================
from rest_framework import serializers
from .models import Inspection, PunchItem


class PunchItemSerializer(serializers.ModelSerializer):
    closed_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = PunchItem
        fields = [
            'id', 'inspection', 'description', 'status',
            'raised_by', 'closed_by', 'closed_by_name', 'closed_at',
            'remarks', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'closed_by_name', 'closed_at']

    def get_closed_by_name(self, obj):
        if obj.closed_by:
            return obj.closed_by.full_name or obj.closed_by.username
        return None


class InspectionSerializer(serializers.ModelSerializer):
    punch_items      = PunchItemSerializer(many=True, read_only=True)
    open_punch_count = serializers.IntegerField(source='open_punch_total', read_only=True)
    created_by_name  = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = Inspection
        fields = [
            'id', 'loco_number', 'loco_class', 'inspection_type',
            'inspection_date', 'inspector', 'status', 'remarks',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'punch_items', 'open_punch_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at',
                            'created_by_name', 'open_punch_count', 'punch_items']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.full_name or obj.created_by.username
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class InspectionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view — excludes nested punch_items."""
    open_punch_count = serializers.IntegerField(source='open_punch_total', read_only=True)
    created_by_name  = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = Inspection
        fields = [
            'id', 'loco_number', 'loco_class', 'inspection_type',
            'inspection_date', 'inspector', 'status', 'remarks',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'open_punch_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at',
                            'created_by_name', 'open_punch_count']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.full_name or obj.created_by.username
        return None
