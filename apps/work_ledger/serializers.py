# =============================================================================
# FILE: apps/work_ledger/serializers.py
# =============================================================================
from rest_framework import serializers
from apps.pl_master.models import PLMaster
from .models import (
    EffortUnit,
    PriorityLevel,
    WorkCategory,
    WorkEntry,
    WorkEntryAttachment,
    WorkTarget,
    WorkType,
    WorkVerification,
)


class WorkCategorySerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='name', read_only=True)

    class Meta:
        model  = WorkCategory
        fields = [
            'id', 'name', 'label', 'code', 'work_type',
            'description', 'is_active', 'sort_order',
        ]


class WorkVerificationSerializer(serializers.ModelSerializer):
    verifier_name = serializers.CharField(
        source='verifier.full_name', read_only=True
    )

    class Meta:
        model  = WorkVerification
        fields = ['id', 'verifier', 'verifier_name', 'action', 'remarks', 'verified_at']
        read_only_fields = ['verified_at']


class WorkEntryAttachmentSerializer(serializers.ModelSerializer):
    attachment_id = serializers.IntegerField(source='id', read_only=True)
    document_id = serializers.SerializerMethodField(read_only=True)
    mime_type = serializers.SerializerMethodField(read_only=True)
    file_size_kb = serializers.SerializerMethodField(read_only=True)

    def get_document_id(self, obj):
        return None

    def get_mime_type(self, obj):
        name = obj.file_name or ''
        if '.' not in name:
            return None
        ext = name.rsplit('.', 1)[-1].lower()
        return {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }.get(ext)

    def get_file_size_kb(self, obj):
        if not obj.file_size:
            return None
        return round(obj.file_size / 1024, 1)

    class Meta:
        model = WorkEntryAttachment
        fields = [
            'attachment_id', 'document_id', 'file_name', 'mime_type',
            'file_size_kb', 'id', 'file', 'file_size', 'description', 'uploaded_at',
        ]
        read_only_fields = ['file_size', 'file_name', 'uploaded_at']


# --- Read (full nested) ----------------------------------------------------
class WorkEntryReadSerializer(serializers.ModelSerializer):
    work_id = serializers.IntegerField(source='id', read_only=True)
    work_code = serializers.SerializerMethodField(read_only=True)
    user_name     = serializers.CharField(
        source='user.full_name', read_only=True
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
        source='submitted_to.full_name', read_only=True
    )
    received_date = serializers.DateField(source='work_date', read_only=True)
    closed_date = serializers.SerializerMethodField(read_only=True)
    section = serializers.CharField(source='user.section.name', read_only=True)
    engineer_id = serializers.IntegerField(source='user_id', read_only=True)
    officer_id = serializers.IntegerField(source='submitted_to_id', read_only=True)
    pl_number = serializers.CharField(source='linked_pl_number_id', read_only=True)
    drawing_number = serializers.CharField(source='linked_drawing_number', read_only=True)
    tender_number = serializers.CharField(source='linked_case_no', read_only=True)
    work_category_code = serializers.CharField(source='category.code', read_only=True)
    work_category_label = serializers.CharField(source='category.name', read_only=True)
    case_number = serializers.CharField(source='linked_case_no', read_only=True)
    eoffice_file_no = serializers.CharField(source='reference_number', read_only=True)
    details = serializers.SerializerMethodField(read_only=True)
    drawing_revision = serializers.SerializerMethodField(read_only=True)
    specification_number = serializers.SerializerMethodField(read_only=True)
    specification_revision = serializers.SerializerMethodField(read_only=True)

    def get_work_code(self, obj):
        return f'WL-{obj.pk:05d}'

    def get_closed_date(self, obj):
        return None

    def get_details(self, obj):
        return []

    def get_drawing_revision(self, obj):
        return None

    def get_specification_number(self, obj):
        return None

    def get_specification_revision(self, obj):
        return None

    class Meta:
        model  = WorkEntry
        fields = [
            'work_id', 'work_code', 'received_date', 'closed_date', 'section',
            'engineer_id', 'officer_id', 'pl_number', 'drawing_number',
            'drawing_revision', 'specification_number', 'specification_revision',
            'tender_number', 'work_category_code', 'work_category_label',
            'case_number', 'eoffice_file_no', 'details',
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
    received_date = serializers.DateField(write_only=True, required=False)
    closed_date = serializers.DateField(write_only=True, required=False, allow_null=True)
    section = serializers.CharField(write_only=True, required=False, allow_blank=True)
    engineer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    officer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    status = serializers.CharField(write_only=True, required=False, allow_blank=True)
    pl_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    drawing_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    drawing_revision = serializers.CharField(write_only=True, required=False, allow_blank=True)
    specification_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    specification_revision = serializers.CharField(write_only=True, required=False, allow_blank=True)
    tender_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    case_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    work_category_code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    eoffice_file_no = serializers.CharField(write_only=True, required=False, allow_blank=True)
    details = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model  = WorkEntry
        fields = [
            'id', 'work_date', 'category', 'work_type', 'priority',
            'description', 'reference_number', 'remarks',
            'effort_value', 'effort_unit',
            'linked_pl_number', 'linked_drawing_number',
            'linked_case_no', 'linked_sdr_no',
            'closed_date', 'section', 'engineer_id', 'officer_id', 'status',
            'received_date', 'pl_number', 'drawing_number',
            'drawing_revision', 'specification_number', 'specification_revision',
            'tender_number', 'case_number', 'work_category_code', 'eoffice_file_no',
            'details',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'work_date': {'required': False},
            'category': {'required': False, 'allow_null': True},
            'work_type': {'required': False},
            'priority': {'required': False},
            'reference_number': {'required': False, 'allow_blank': True},
            'remarks': {'required': False, 'allow_blank': True},
            'effort_value': {'required': False, 'allow_null': True},
            'effort_unit': {'required': False, 'allow_blank': True},
            'linked_pl_number': {'required': False, 'allow_null': True},
            'linked_drawing_number': {'required': False, 'allow_blank': True},
            'linked_case_no': {'required': False, 'allow_blank': True},
            'linked_sdr_no': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)

        received_date = self.initial_data.get('received_date')
        if not attrs.get('work_date') and received_date:
            attrs['work_date'] = received_date

        category_code = (self.initial_data.get('work_category_code') or '').strip()
        if not attrs.get('category') and category_code:
            category = WorkCategory.objects.filter(code=category_code, is_active=True).first()
            if category is None:
                raise serializers.ValidationError({'work_category_code': 'Unknown work category code.'})
            attrs['category'] = category

        if not attrs.get('work_type'):
            attrs['work_type'] = attrs['category'].work_type if attrs.get('category') else WorkType.OTHER

        attrs.setdefault('priority', PriorityLevel.ROUTINE)
        attrs.setdefault('effort_unit', EffortUnit.HOURS)

        pl_number = (self.initial_data.get('pl_number') or '').strip()
        if not attrs.get('linked_pl_number') and pl_number:
            linked_pl = PLMaster.objects.filter(pl_number=pl_number).first()
            if linked_pl is None:
                raise serializers.ValidationError({'pl_number': 'Unknown PL number.'})
            attrs['linked_pl_number'] = linked_pl

        if not attrs.get('linked_drawing_number'):
            attrs['linked_drawing_number'] = (self.initial_data.get('drawing_number') or '').strip()

        case_reference = (
            self.initial_data.get('case_number')
            or self.initial_data.get('tender_number')
            or ''
        ).strip()
        if not attrs.get('linked_case_no') and case_reference:
            attrs['linked_case_no'] = case_reference

        if not attrs.get('reference_number'):
            attrs['reference_number'] = (self.initial_data.get('eoffice_file_no') or '').strip()

        raw_status = (self.initial_data.get('status') or '').strip().upper()
        if raw_status in {'OPEN', 'DRAFT'}:
            attrs['status'] = 'DRAFT'
        elif raw_status in {'PENDING', 'SUBMITTED'}:
            attrs['status'] = 'SUBMITTED'
        elif raw_status in {'CLOSED', 'APPROVED'}:
            attrs['status'] = 'APPROVED'
        elif raw_status == 'RETURNED':
            attrs['status'] = 'RETURNED'

        for transient_field in (
            'received_date',
            'closed_date',
            'section',
            'engineer_id',
            'officer_id',
            'pl_number',
            'drawing_number',
            'drawing_revision',
            'specification_number',
            'specification_revision',
            'tender_number',
            'case_number',
            'work_category_code',
            'eoffice_file_no',
            'details',
        ):
            attrs.pop(transient_field, None)

        return attrs

    def validate_work_date(self, value):
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError('Work date cannot be in the future.')
        return value

    def create(self, validated_data):
        validated_data['user']   = self.context['request'].user
        validated_data.setdefault('status', 'DRAFT')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


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
    user_name   = serializers.CharField(source='user.full_name', read_only=True)
    set_by_name = serializers.CharField(source='set_by.full_name', read_only=True)
    work_type_display  = serializers.CharField(source='get_work_type_display', read_only=True)
    target_unit_display = serializers.CharField(source='get_target_unit_display', read_only=True)

    class Meta:
        model  = WorkTarget
        fields = '__all__'
        read_only_fields = ['created_at']
