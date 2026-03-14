# =============================================================================
# FILE: apps/sdr/serializers.py
# =============================================================================
from rest_framework import serializers
from .models import SDRRecord, SDRItem


class SDRItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SDRItem
        fields = [
            'id',
            'document_type',
            'drawing',
            'specification',
            'document_number',
            'document_title',
            'alteration_no',
            'size',
            'copies',
            'controlled_copy',
        ]

    def validate(self, data):
        doc_type = data.get('document_type', 'DRAWING')
        if doc_type == 'DRAWING' and not data.get('drawing'):
            raise serializers.ValidationError('drawing is required when document_type is DRAWING.')
        if doc_type == 'SPEC' and not data.get('specification'):
            raise serializers.ValidationError('specification is required when document_type is SPEC.')
        return data


class SDRRecordSerializer(serializers.ModelSerializer):
    items = SDRItemSerializer(many=True)

    # Read-only computed
    total_items        = serializers.ReadOnlyField()
    has_controlled_copy = serializers.ReadOnlyField()

    class Meta:
        model  = SDRRecord
        fields = [
            'id',
            'sdr_number',
            'issue_date',
            'shop_name',
            'requesting_official',
            'issuing_official',
            'receiving_official',
            'remarks',
            'items',
            'total_items',
            'has_controlled_copy',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['sdr_number', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        record = SDRRecord.objects.create(**validated_data)
        for item_data in items_data:
            SDRItem.objects.create(sdr_record=record, **item_data)
        return record

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                SDRItem.objects.create(sdr_record=instance, **item_data)
        return instance


class SDRRecordListSerializer(serializers.ModelSerializer):
    """Lightweight list serializer — no nested items."""
    total_items         = serializers.ReadOnlyField()
    has_controlled_copy = serializers.ReadOnlyField()

    class Meta:
        model  = SDRRecord
        fields = [
            'id', 'sdr_number', 'issue_date',
            'shop_name', 'requesting_official',
            'issuing_official', 'receiving_official',
            'total_items', 'has_controlled_copy',
            'created_at',
        ]
