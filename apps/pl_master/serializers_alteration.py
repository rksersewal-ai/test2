# =============================================================================
# FILE: apps/pl_master/serializers_alteration.py
# =============================================================================
from rest_framework import serializers
from apps.pl_master.models import AlterationHistory


class AlterationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = AlterationHistory
        fields = [
            'id',
            'document_type',
            'document_number',
            'alteration_number',
            'previous_alteration',
            'alteration_date',
            'changes_description',
            'probable_impacts',
            'source_agency',
            'affected_pl_numbers',
            'implementation_status',
            'implementation_remarks',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
