# =============================================================================
# FILE: apps/sanity/serializers.py
# SPRINT 6
# =============================================================================
from rest_framework import serializers
from apps.sanity.models import SanityReport


class SanityReportSerializer(serializers.ModelSerializer):
    run_by_name = serializers.CharField(
        source='run_by.get_full_name', read_only=True
    )

    class Meta:
        model  = SanityReport
        fields = [
            'id', 'run_by', 'run_by_name', 'ran_at',
            'total_issues', 'error_count', 'warning_count', 'info_count',
            'issues', 'stale_draft_days',
        ]
        read_only_fields = fields


class RunSanitySerializer(serializers.Serializer):
    """Input for POST /api/sanity/run/"""
    stale_draft_days = serializers.IntegerField(default=90, min_value=1)
