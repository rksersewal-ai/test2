"""Workflow / LDO Work Ledger serializers."""
from rest_framework import serializers
from apps.workflow.models import WorkLedger, WorkType, Vendor, Tender


class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = ['id', 'code', 'name', 'description', 'is_active']


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'code', 'name', 'address', 'contact', 'is_active']


class TenderSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = Tender
        fields = [
            'id', 'tender_number', 'title', 'description', 'status',
            'issue_date', 'closing_date', 'eoffice_file_number',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WorkLedgerSerializer(serializers.ModelSerializer):
    work_type_name = serializers.CharField(source='work_type.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    document_number = serializers.CharField(source='document.document_number', read_only=True)
    tender_number = serializers.CharField(source='tender.tender_number', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = WorkLedger
        fields = [
            'id', 'work_type', 'work_type_name', 'section', 'section_name',
            'assigned_to', 'assigned_to_name', 'status',
            'received_date', 'target_date', 'closed_date',
            'eoffice_file_number', 'eoffice_subject',
            'document', 'document_number', 'revision', 'tender', 'tender_number',
            'vendor', 'vendor_name', 'subject', 'remarks',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
