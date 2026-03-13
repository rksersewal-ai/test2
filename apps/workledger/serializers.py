from rest_framework import serializers
from .models import WorkLedger, WorkLedgerDetail, WorkLedgerAttachment, WorkCategoryMaster


class WorkCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCategoryMaster
        fields = ["code", "label", "sort_order"]


class WorkLedgerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLedgerDetail
        fields = ["field_name", "field_value"]


class WorkLedgerAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLedgerAttachment
        fields = ["attachment_id", "document_id", "file_name", "mime_type", "file_size_kb", "uploaded_at"]
        read_only_fields = ["attachment_id", "uploaded_at"]


class WorkLedgerListSerializer(serializers.ModelSerializer):
    work_category_label = serializers.SerializerMethodField()

    class Meta:
        model = WorkLedger
        fields = [
            "work_id", "work_code", "received_date", "closed_date",
            "section", "status", "pl_number", "drawing_number",
            "tender_number", "work_category_code", "work_category_label",
            "description", "remarks", "created_at",
        ]

    def get_work_category_label(self, obj):
        try:
            return WorkCategoryMaster.objects.get(code=obj.work_category_code).label
        except WorkCategoryMaster.DoesNotExist:
            return obj.work_category_code


class WorkLedgerDetailReadSerializer(WorkLedgerListSerializer):
    details = WorkLedgerDetailSerializer(many=True, read_only=True)
    attachments = WorkLedgerAttachmentSerializer(many=True, read_only=True)

    class Meta(WorkLedgerListSerializer.Meta):
        fields = WorkLedgerListSerializer.Meta.fields + [
            "engineer_id", "officer_id", "drawing_revision",
            "specification_number", "specification_revision",
            "case_number", "eoffice_file_no", "details", "attachments",
        ]


class WorkLedgerWriteSerializer(serializers.ModelSerializer):
    details = WorkLedgerDetailSerializer(many=True, required=False)

    class Meta:
        model = WorkLedger
        fields = [
            "received_date", "closed_date", "section", "engineer_id",
            "officer_id", "status", "pl_number", "drawing_number",
            "drawing_revision", "specification_number", "specification_revision",
            "tender_number", "case_number", "eoffice_file_no",
            "work_category_code", "description", "remarks", "details",
        ]

    def validate(self, data):
        if data.get("status") == "Closed" and not data.get("closed_date"):
            raise serializers.ValidationError(
                {"closed_date": "Closed date is required when status is Closed."}
            )
        if data.get("closed_date") and data.get("received_date"):
            if data["closed_date"] < data["received_date"]:
                raise serializers.ValidationError(
                    {"closed_date": "Closed date cannot be before received date."}
                )
        return data


class ActivityReportRowSerializer(serializers.Serializer):
    work_id = serializers.IntegerField()
    work_code = serializers.CharField()
    received_date = serializers.DateField()
    closed_date = serializers.DateField(allow_null=True)
    section = serializers.CharField()
    engineer_name = serializers.CharField(allow_null=True)
    officer_name = serializers.CharField(allow_null=True)
    work_category_label = serializers.CharField()
    pl_number = serializers.CharField(allow_null=True)
    drawing_number = serializers.CharField(allow_null=True)
    tender_number = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    remarks = serializers.CharField(allow_null=True)


class KpiSummaryRowSerializer(serializers.Serializer):
    work_category_code = serializers.CharField()
    work_category_label = serializers.CharField()
    work_count = serializers.IntegerField()
