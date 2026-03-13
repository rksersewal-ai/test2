# =============================================================================
# FILE: apps/workflow/serializers.py
# SPRINT 4: Added Approval serializers.
# All Sprint 1 serializers preserved exactly.
# =============================================================================
from rest_framework import serializers
from apps.workflow.models import (
    WorkType, WorkLedgerEntry,
    ApprovalChain, ApprovalStep, ApprovalRequest, ApprovalVote,
)


# ---- Sprint 1 (preserved) ---------------------------------------------------

class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WorkType
        fields = ['id', 'name', 'code', 'description', 'is_active']


class WorkLedgerListSerializer(serializers.ModelSerializer):
    work_type_name  = serializers.CharField(source='work_type.name',  read_only=True)
    section_name    = serializers.CharField(source='section.name',    read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)

    class Meta:
        model  = WorkLedgerEntry
        fields = [
            'id', 'work_type', 'work_type_name', 'subject', 'status',
            'section', 'section_name', 'assigned_to', 'assigned_to_name',
            'eoffice_file_number', 'received_date', 'target_date', 'closed_date',
            'created_at',
        ]


class WorkLedgerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WorkLedgerEntry
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']


# ---- Sprint 4: Approval Engine ----------------------------------------------

class ApprovalStepSerializer(serializers.ModelSerializer):
    assigned_user_name = serializers.CharField(
        source='assigned_user.get_full_name', read_only=True
    )

    class Meta:
        model  = ApprovalStep
        fields = [
            'id', 'chain', 'step_order', 'label', 'role',
            'assigned_user', 'assigned_user_name',
            'due_days', 'is_optional',
        ]


class ApprovalChainSerializer(serializers.ModelSerializer):
    steps              = ApprovalStepSerializer(many=True, read_only=True)
    document_type_name = serializers.CharField(
        source='document_type.name', read_only=True
    )
    created_by_name    = serializers.CharField(
        source='created_by.get_full_name', read_only=True
    )

    class Meta:
        model  = ApprovalChain
        fields = [
            'id', 'name', 'document_type', 'document_type_name',
            'is_active', 'steps', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class ApprovalVoteSerializer(serializers.ModelSerializer):
    voted_by_name = serializers.CharField(
        source='voted_by.get_full_name', read_only=True
    )
    step_label    = serializers.CharField(source='step.label', read_only=True)

    class Meta:
        model  = ApprovalVote
        fields = [
            'id', 'request', 'step', 'step_label',
            'voted_by', 'voted_by_name', 'vote', 'comment', 'voted_at',
        ]
        read_only_fields = ['voted_by', 'voted_at']


class ApprovalRequestListSerializer(serializers.ModelSerializer):
    chain_name         = serializers.CharField(source='chain.name',    read_only=True)
    initiated_by_name  = serializers.CharField(
        source='initiated_by.get_full_name', read_only=True
    )
    revision_label     = serializers.SerializerMethodField()

    def get_revision_label(self, obj):
        try:
            return (
                f'{obj.revision.document.document_number} '
                f'Rev {obj.revision.revision_number}'
            )
        except Exception:
            return str(obj.revision_id)

    class Meta:
        model  = ApprovalRequest
        fields = [
            'id', 'chain', 'chain_name', 'revision', 'revision_label',
            'status', 'current_step', 'initiated_by', 'initiated_by_name',
            'initiated_at', 'completed_at',
        ]


class ApprovalRequestDetailSerializer(serializers.ModelSerializer):
    votes              = ApprovalVoteSerializer(many=True, read_only=True)
    chain_name         = serializers.CharField(source='chain.name',    read_only=True)
    initiated_by_name  = serializers.CharField(
        source='initiated_by.get_full_name', read_only=True
    )

    class Meta:
        model  = ApprovalRequest
        fields = [
            'id', 'chain', 'chain_name', 'revision', 'status',
            'current_step', 'initiated_by', 'initiated_by_name',
            'initiated_at', 'completed_at', 'remarks', 'votes',
        ]
        read_only_fields = [
            'initiated_by', 'initiated_at', 'completed_at', 'current_step',
        ]


class CastVoteSerializer(serializers.Serializer):
    """Input payload for POST /approval-requests/{id}/vote/"""
    vote    = serializers.ChoiceField(choices=ApprovalVote.Vote.choices)
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class InitiateApprovalSerializer(serializers.Serializer):
    """Input payload for POST /approval-requests/initiate/"""
    chain_id    = serializers.IntegerField()
    revision_id = serializers.IntegerField()
    remarks     = serializers.CharField(required=False, allow_blank=True, default='')
