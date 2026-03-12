from rest_framework import serializers
from apps.workflow.models import WorkType, WorkLedgerEntry


class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = ['id', 'name', 'code', 'description', 'is_active']


class WorkLedgerListSerializer(serializers.ModelSerializer):
    work_type_name = serializers.CharField(source='work_type.name', read_only=True, default=None)
    section_name = serializers.CharField(source='section.name', read_only=True, default=None)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = WorkLedgerEntry
        fields = [
            'id', 'subject', 'eoffice_subject', 'eoffice_file_number',
            'work_type', 'work_type_name',
            'section', 'section_name',
            'assigned_to', 'assigned_to_name',
            'status', 'received_date', 'target_date', 'closed_date',
            'created_at', 'updated_at',
        ]

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else None


class WorkLedgerDetailSerializer(serializers.ModelSerializer):
    work_type_name = serializers.CharField(source='work_type.name', read_only=True, default=None)
    section_name = serializers.CharField(source='section.name', read_only=True, default=None)
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = WorkLedgerEntry
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else None

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None
