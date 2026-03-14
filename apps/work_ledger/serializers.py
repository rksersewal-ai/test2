# =============================================================================
# FILE: apps/work_ledger/serializers.py
# =============================================================================
from rest_framework import serializers
from .models import WorkCategory, WorkEntry, WorkEntryAttachment, WorkVerification, WorkTarget


class WorkCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = WorkCategory
        fields = '__all__'


class WorkVerificationSerializer(serializers.ModelSerializer):
    verifier_name = serializers.CharField(
        source='verifier.get_full_name', read_only=True
    )

    class Meta:
        model  = WorkVerification
        fields = ['id', 'verifier', 'verifier_name', 'action', 'remarks', 'verified_at']
        read_only_fields = ['verified_at']


class WorkEntryAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WorkEntryAttachment
        fields = ['id', 'file', 'file_name', 'file_size', 'description', 'uploaded_at']
        read_only_fields = ['file_size', 'file_name', 'uploaded_at']


# --- Read (full nested) ----------------------------------------------------
class WorkEntryReadSerializer(serializers.ModelSerializer):
    user_name     = serializers.CharField(
        source='user.get_full_name', read_only=True
    )
    user_designation = serializers.CharField(
        source='user.designation', read_only=True
    )
    category_name = serializers.CharField(
        source='category.name', read_only=True
    )
    work_type_display    = serializers.CharField(
        source='get_work_type_display', read_only=True
    )
    status_display       = serializers.CharField(
        source='get_status_display', read_only=True
    )
    priority_display     = serializers.CharField(
        source='get_priority_display', read_only=True
    )
    effort_unit_display  = serializers.CharField(
        source='get_effort_unit_display', read_only=True
    )
    verifications = WorkVerificationSerializer(many=True, read_only=True)
    attachments   = WorkEntryAttachmentSerializer(many=True, read_only=True)
    submitted_to_name = serializers.CharField(
        source='submitted_to.get_full_name', read_only=True
    )

    class Meta:
        model  = WorkEntry
        fields = [
            'id', 'user', 'user_name', 'user_designation',
            'work_date', 'category', 'category_name',
            'work_type', 'work_type_display',
            'priority', 'priority_display',
            'description', 'reference_number', 'remarks',
            'effort_value', 'effort_unit', 'effort_unit_display',
            'linked_pl_number', 'linked_drawing_number',
            'linked_case_no', 'linked_sdr_no',
            'status', 'status_display',
            'submitted_at', 'submitted_to', 'submitted_to_name',
            'created_at', 'updated_at',
            'verifications', 'attachments',
        ]


# --- Write -----------------------------------------------------------------
class WorkEntryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WorkEntry
        fields = [
            'id', 'work_date', 'category', 'work_type', 'priority',
            'description', 'reference_number', 'remarks',
            'effort_value', 'effort_unit',
            'linked_pl_number', 'linked_drawing_number',
            'linked_case_no', 'linked_sdr_no',
        ]
        read_only_fields = ['id']

    def validate_work_date(self, value):
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError('Work date cannot be in the future.')
        return value

    def create(self, validated_data):
        validated_data['user']   = self.context['request'].user
        validated_data['status'] = 'DRAFT'
        return super().create(validated_data)


# --- Submit action payload --------------------------------------------------
class WorkEntrySubmitSerializer(serializers.Serializer):
    supervisor_id = serializers.IntegerField(
        help_text='User ID of the supervisor to submit to for verification'
    )


# --- Verify/Return payload -------------------------------------------------
class WorkEntryVerifySerializer(serializers.Serializer):
    action  = serializers.ChoiceField(
        choices=[('VERIFIED', 'Verified'), ('RETURNED', 'Returned'), ('APPROVED', 'Approved')]
    )
    remarks = serializers.CharField(required=False, allow_blank=True, default='')


# --- WorkTarget ------------------------------------------------------------
class WorkTargetSerializer(serializers.ModelSerializer):
    user_name   = serializers.CharField(source='user.get_full_name', read_only=True)
    set_by_name = serializers.CharField(source='set_by.get_full_name', read_only=True)
    work_type_display  = serializers.CharField(source='get_work_type_display', read_only=True)
    target_unit_display = serializers.CharField(source='get_target_unit_display', read_only=True)

    class Meta:
        model  = WorkTarget
        fields = '__all__'
        read_only_fields = ['created_at']
