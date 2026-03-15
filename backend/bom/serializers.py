from rest_framework import serializers
from .models import BOMTree, BOMNode, BOMSnapshot


class BOMTreeSerializer(serializers.ModelSerializer):
    node_count = serializers.SerializerMethodField()

    class Meta:
        model = BOMTree
        fields = ['id', 'loco_type', 'variant', 'description', 'is_active',
                  'node_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'node_count', 'created_at', 'updated_at']

    def get_node_count(self, obj):
        return obj.nodes.filter(is_active=True).count()


class BOMNodeSerializer(serializers.ModelSerializer):
    created_by_name      = serializers.SerializerMethodField()
    updated_by_name      = serializers.SerializerMethodField()
    node_type_label      = serializers.SerializerMethodField()
    inspection_cat_label = serializers.SerializerMethodField()
    children_count       = serializers.SerializerMethodField()

    class Meta:
        model = BOMNode
        fields = [
            'id', 'tree', 'parent', 'pl_number', 'description',
            'node_type', 'node_type_label', 'inspection_category', 'inspection_cat_label',
            'safety_item', 'quantity', 'unit', 'position', 'level',
            'canvas_x', 'canvas_y', 'is_active', 'remarks',
            'children_count', 'created_by_name', 'updated_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'level', 'node_type_label', 'inspection_cat_label',
            'children_count', 'created_by_name', 'updated_by_name', 'created_at', 'updated_at',
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.username if obj.created_by else ''

    def get_updated_by_name(self, obj):
        return obj.updated_by.get_full_name() or obj.updated_by.username if obj.updated_by else ''

    def get_node_type_label(self, obj):
        return obj.get_node_type_display()

    def get_inspection_cat_label(self, obj):
        return obj.get_inspection_category_display()

    def get_children_count(self, obj):
        return obj.children.filter(is_active=True).count()


class BOMSnapshotSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = BOMSnapshot
        fields = ['id', 'tree', 'name', 'description', 'snapshot_data', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'snapshot_data', 'created_by_name', 'created_at']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.username if obj.created_by else ''
