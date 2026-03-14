# =============================================================================
# FILE: backend/master/serializers_pl_docs.py
# SERIALIZERS for PLVendorInfo and PLLinkedDocument
# =============================================================================
from rest_framework import serializers
from .models_pl_docs import PLVendorInfo, PLLinkedDocument


class PLVendorInfoSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.SerializerMethodField()
    word_count      = serializers.SerializerMethodField()

    class Meta:
        model  = PLVendorInfo
        fields = [
            'id', 'pl_number', 'vendor_type',
            'uvam_vd_number', 'eligibility_criteria',
            'word_count', 'updated_by_name', 'updated_at',
        ]
        read_only_fields = ['id', 'pl_number', 'updated_by_name', 'updated_at', 'word_count']

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return obj.updated_by.get_full_name() or obj.updated_by.username
        return ''

    def get_word_count(self, obj):
        return len(obj.eligibility_criteria.split()) if obj.eligibility_criteria else 0

    def validate(self, attrs):
        vendor_type = attrs.get('vendor_type', getattr(self.instance, 'vendor_type', 'NVD'))
        uvam        = attrs.get('uvam_vd_number', getattr(self.instance, 'uvam_vd_number', ''))
        eligibility = attrs.get('eligibility_criteria', getattr(self.instance, 'eligibility_criteria', ''))

        if vendor_type == 'VD' and not uvam.strip():
            raise serializers.ValidationError({'uvam_vd_number': 'UVAM VD Number is required for VD parts.'})

        if vendor_type == 'NVD':
            wc = len(eligibility.split())
            if wc > 2000:
                raise serializers.ValidationError(
                    {'eligibility_criteria': f'Exceeds 2000-word limit (current: {wc} words).'}
                )
        return attrs


class PLLinkedDocumentSerializer(serializers.ModelSerializer):
    linked_by_name = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()

    class Meta:
        model  = PLLinkedDocument
        fields = [
            'id', 'pl_number', 'document_id',
            'document_title', 'document_number', 'category', 'category_label',
            'remarks', 'linked_by_name', 'linked_at',
        ]
        read_only_fields = ['id', 'pl_number', 'linked_by_name', 'linked_at', 'category_label']

    def get_linked_by_name(self, obj):
        if obj.linked_by:
            return obj.linked_by.get_full_name() or obj.linked_by.username
        return ''

    def get_category_label(self, obj):
        return obj.get_category_display()
