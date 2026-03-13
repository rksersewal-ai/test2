from django.db import models
from django.utils import timezone


class WorkCategoryMaster(models.Model):
    code = models.CharField(max_length=60, primary_key=True)
    label = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "work_category_master"
        ordering = ["sort_order"]
        managed = False  # managed by sql/004_work_ledger_core.sql

    def __str__(self):
        return self.label


class WorkLedger(models.Model):
    SECTION_CHOICES = [
        ("Mechanical", "Mechanical"),
        ("Electrical", "Electrical"),
        ("General", "General"),
    ]
    STATUS_CHOICES = [
        ("Open", "Open"),
        ("Closed", "Closed"),
        ("Pending", "Pending"),
    ]

    work_id = models.BigAutoField(primary_key=True)
    work_code = models.CharField(max_length=30, unique=True)
    received_date = models.DateField()
    closed_date = models.DateField(null=True, blank=True)
    section = models.CharField(max_length=30, choices=SECTION_CHOICES)
    engineer_id = models.BigIntegerField()
    officer_id = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Open")
    pl_number = models.CharField(max_length=60, null=True, blank=True)
    drawing_number = models.CharField(max_length=120, null=True, blank=True)
    drawing_revision = models.CharField(max_length=20, null=True, blank=True)
    specification_number = models.CharField(max_length=120, null=True, blank=True)
    specification_revision = models.CharField(max_length=20, null=True, blank=True)
    tender_number = models.CharField(max_length=120, null=True, blank=True)
    case_number = models.CharField(max_length=120, null=True, blank=True)
    eoffice_file_no = models.CharField(max_length=120, null=True, blank=True)
    work_category_code = models.CharField(max_length=60)
    description = models.TextField()
    remarks = models.TextField(null=True, blank=True)
    created_by = models.BigIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "work_ledger"
        ordering = ["-received_date", "-work_id"]
        managed = False

    def __str__(self):
        return self.work_code


class WorkLedgerDetail(models.Model):
    detail_id = models.BigAutoField(primary_key=True)
    work = models.ForeignKey(
        WorkLedger,
        on_delete=models.CASCADE,
        related_name="details",
        db_column="work_id",
    )
    field_name = models.CharField(max_length=100)
    field_value = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "work_ledger_detail"
        unique_together = [("work", "field_name")]
        managed = False

    def __str__(self):
        return f"{self.work_id} | {self.field_name}"


class WorkLedgerAttachment(models.Model):
    attachment_id = models.BigAutoField(primary_key=True)
    work = models.ForeignKey(
        WorkLedger,
        on_delete=models.CASCADE,
        related_name="attachments",
        db_column="work_id",
    )
    document_id = models.BigIntegerField(null=True, blank=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=600)
    mime_type = models.CharField(max_length=100, null=True, blank=True)
    file_size_kb = models.IntegerField(null=True, blank=True)
    uploaded_by = models.BigIntegerField()
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "work_ledger_attachment"
        managed = False

    def __str__(self):
        return self.file_name
