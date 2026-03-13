from rest_framework import serializers
from .models import LocomotiveType, ComponentCatalog, LookupCategory, LookupItem, MasterDataChangeLog


class LocomotiveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LocomotiveType
        fields = [
            'id', 'model_id', 'name', 'loco_class', 'status',
            'engine_power', 'engine_type', 'manufacturer', 'year_introduced',
            'notes', 'created_at', 'updated_at',
        ]


class LookupItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LookupItem
        fields = ['id', 'label', 'value', 'color', 'order', 'is_active']


class LookupCategorySerializer(serializers.ModelSerializer):
    items       = LookupItemSerializer(many=True, read_only=True)
    item_count  = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model  = LookupCategory
        fields = ['id', 'name', 'code', 'description', 'item_count', 'items']


class MasterDataChangeLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model  = MasterDataChangeLog
        fields = ['id', 'action', 'model_name', 'description', 'detail', 'user_name', 'timestamp']


class ComponentCatalogSerializer(serializers.ModelSerializer):
    applicable_loco_ids = serializers.PrimaryKeyRelatedField(
        source='applicable_locos', many=True, read_only=True
    )

    class Meta:
        model  = ComponentCatalog
        fields = [
            'id', 'part_number', 'description', 'category', 'status',
            'supplier', 'unit', 'unit_price', 'applicable_loco_ids', 'notes',
            'created_at', 'updated_at',
        ]
