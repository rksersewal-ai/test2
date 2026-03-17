# =============================================================================
# FILE: apps/pl_master/models.py
# PRD Reference: PLW/LDO/PRD/2026/001 v1.0 — Sections 13.1 to 13.9
#
# Models:
#   ControllingAgency      — master table for CLW/BLW/RDSO/ICF/PLW
#   PLMaster               — 50,000+ PL items, core of the system
#   DrawingMaster          — 600,000+ drawings with 14 types & alteration tracking
#   SpecificationMaster    — 12 spec types with alteration tracking
#   VendorDrawing          — vendor drawings with approval workflow
#   STRMaster              — Stores Type Register
#   RDSOReference          — RDSO MS/SMI/SPEC/STD_DRG/MP documents
#   AlterationHistory      — unified alteration log across all doc types
#   PLDrawingLink          — M2M: PL ↔ Drawing (with metadata)
#   PLSpecLink             — M2M: PL ↔ Specification (with metadata)
#   PLStandardLink         — M2M: PL ↔ Standard/RDSO Reference (with metadata)
#   PLSMILink              — M2M: PL ↔ SMI (with metadata)
#   PLAlternate            — interchangeable/alternative PL numbers
#   PLLocoApplicability    — per-loco-type applicability record
# =============================================================================
from django.conf import settings
from django.db import models


AUTH_USER = settings.AUTH_USER_MODEL


# ---------------------------------------------------------------------------
# Controlling Agency master
# ---------------------------------------------------------------------------
class ControllingAgency(models.Model):
    agency_code   = models.CharField(max_length=10, unique=True)
    agency_name   = models.CharField(max_length=100)
    agency_type   = models.CharField(max_length=50, blank=True)  # Production Unit / Design Office
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address       = models.TextField(blank=True)
    is_active     = models.BooleanField(default=True)

    class Meta:
        db_table = 'pl_controlling_agency'
        ordering = ['agency_code']

    def __str__(self):
        return self.agency_code


# ---------------------------------------------------------------------------
# PL Master  — the central entity
# ---------------------------------------------------------------------------
class PLMaster(models.Model):

    class InspectionCategory(models.TextChoices):
        CAT_A = 'CAT-A', 'CAT-A (Most Critical)'
        CAT_B = 'CAT-B', 'CAT-B (Critical)'
        CAT_C = 'CAT-C', 'CAT-C (Important)'
        CAT_D = 'CAT-D', 'CAT-D (General)'

    class SafetyClassification(models.TextChoices):
        CRITICAL = 'CRITICAL', 'Critical'
        HIGH     = 'HIGH',     'High'
        MEDIUM   = 'MEDIUM',   'Medium'
        LOW      = 'LOW',      'Low'

    class SeverityOfFailure(models.TextChoices):
        CATASTROPHIC = 'CATASTROPHIC', 'Catastrophic'
        MAJOR        = 'MAJOR',        'Major'
        MINOR        = 'MINOR',        'Minor'
        NEGLIGIBLE   = 'NEGLIGIBLE',   'Negligible'

    class InspectionAgency(models.TextChoices):
        RITES       = 'RITES',       'RITES'
        SELF        = 'SELF',        'Self Inspection'
        THIRD_PARTY = 'THIRD_PARTY', 'Third Party'

    # --- Identity ---
    pl_number               = models.CharField(max_length=50, unique=True, db_index=True)
    part_description        = models.TextField()
    part_description_hindi  = models.TextField(blank=True)

    # --- BOM Hierarchy ---
    mother_part             = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='child_parts',
        db_column='mother_part_pl_number',
        to_field='pl_number',
    )
    mother_part_description = models.TextField(blank=True)

    # --- Safety ---
    safety_item             = models.BooleanField(default=False)
    safety_classification   = models.CharField(
        max_length=20, choices=SafetyClassification.choices, blank=True
    )
    severity_of_failure     = models.CharField(
        max_length=20, choices=SeverityOfFailure.choices, blank=True
    )
    consequences_upon_failure = models.TextField(blank=True)
    failure_mode            = models.TextField(blank=True)

    # --- Functional ---
    functionality           = models.TextField(blank=True)
    used_in                 = models.JSONField(
        default=list, blank=True,
        help_text='Loco types: WAG9, WAP7, WAP5, MEMU, DEMU ...'
    )
    application_area        = models.CharField(max_length=100, blank=True)

    # --- Inspection ---
    inspection_category     = models.CharField(
        max_length=10, choices=InspectionCategory.choices, blank=True, db_index=True
    )
    stage_inspection_reqd   = models.JSONField(
        default=dict, blank=True,
        help_text='JSONB: {RMS: true, PPS: false, IPS: true, FMS: true, HTS: false, FIS: true}'
    )
    inspection_agency       = models.CharField(
        max_length=20, choices=InspectionAgency.choices, blank=True
    )

    # --- Controlling Agency ---
    controlling_agency      = models.ForeignKey(
        ControllingAgency, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='pl_items',
        to_field='agency_code',
    )
    controlling_pu          = models.CharField(max_length=50, blank=True)
    rdso_controlled         = models.BooleanField(default=False)

    # --- UVAM / Vendor ---
    vd_item                 = models.BooleanField(default=False,  help_text='Vendor Directory item')
    uvam_id                 = models.CharField(max_length=50, blank=True, db_index=True)
    uvam_category           = models.CharField(max_length=50, blank=True)
    nvd_item                = models.BooleanField(default=False, help_text='Non-VD item')

    # --- Set / Kit ---
    set_list_number         = models.CharField(max_length=50, blank=True)
    set_list_description    = models.TextField(blank=True)

    # --- Supervisors ---
    design_supervisor       = models.CharField(max_length=100, blank=True)
    design_supervisor_id    = models.ForeignKey(
        AUTH_USER, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='design_pl_items',
        db_column='design_supervisor_user_id',
    )
    concerned_supervisor    = models.CharField(max_length=100, blank=True)
    concerned_supervisor_id = models.ForeignKey(
        AUTH_USER, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='concerned_pl_items',
        db_column='concerned_supervisor_user_id',
    )

    # --- Reference Numbers ---
    e_office_file_no        = models.CharField(max_length=100, blank=True)
    case_no                 = models.CharField(max_length=100, blank=True)

    # --- Search / Tags ---
    keywords                = models.JSONField(default=list, blank=True)
    tags                    = models.JSONField(default=list, blank=True)
    remarks                 = models.TextField(blank=True)

    # --- Lifecycle ---
    is_active               = models.BooleanField(default=True)
    version                 = models.PositiveIntegerField(default=1)
    created_by              = models.ForeignKey(
        AUTH_USER, null=True, on_delete=models.SET_NULL,
        related_name='pl_created', db_column='created_by_id',
    )
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_by              = models.ForeignKey(
        AUTH_USER, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='pl_updated', db_column='updated_by_id',
    )
    updated_at              = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'pl_master'
        ordering  = ['pl_number']
        indexes   = [
            models.Index(fields=['inspection_category']),
            models.Index(fields=['controlling_agency']),
            models.Index(fields=['safety_item']),
            models.Index(fields=['uvam_id']),
            models.Index(fields=['vd_item']),
        ]

    def __str__(self):
        return f"{self.pl_number} — {self.part_description[:60]}"


# ---------------------------------------------------------------------------
# Drawing Master
# ---------------------------------------------------------------------------
class DrawingMaster(models.Model):

    class DrawingType(models.TextChoices):
        GA = 'GA', 'General Arrangement'
        AD = 'AD', 'Assembly Drawing'
        CD = 'CD', 'Component Drawing'
        SD = 'SD', 'Scheme Drawing'
        WD = 'WD', 'Wiring Diagram'
        PD = 'PD', 'Piping Diagram'
        ID = 'ID', 'Installation Drawing'
        FD = 'FD', 'Foundation Drawing'
        TD = 'TD', 'Tool Drawing'
        JD = 'JD', 'Jig Drawing'
        MD = 'MD', 'Modification Drawing'
        RD = 'RD', 'Repair Drawing'
        BD = 'BD', 'Block Diagram'
        LD = 'LD', 'Layout Drawing'

    class ReadabilityStatus(models.TextChoices):
        READABLE   = 'READABLE',   'Readable'
        PARTIAL    = 'PARTIAL',    'Partial'
        POOR       = 'POOR',       'Poor'
        ILLEGIBLE  = 'ILLEGIBLE',  'Illegible'
        MISSING    = 'MISSING',    'Missing'
        SUPERSEDED = 'SUPERSEDED', 'Superseded'

    class SheetSize(models.TextChoices):
        A0 = 'A0', 'A0'
        A1 = 'A1', 'A1'
        A2 = 'A2', 'A2'
        A3 = 'A3', 'A3'
        A4 = 'A4', 'A4'

    drawing_number          = models.CharField(max_length=100, unique=True, db_index=True)
    drawing_title           = models.CharField(max_length=500)
    drawing_type            = models.CharField(
        max_length=20, choices=DrawingType.choices, blank=True
    )

    # --- Alteration ---
    current_alteration      = models.CharField(max_length=20, blank=True)
    alteration_date         = models.DateField(null=True, blank=True)
    alteration_description  = models.TextField(blank=True)
    probable_impacts        = models.TextField(blank=True)

    # --- Source ---
    controlling_agency      = models.ForeignKey(
        ControllingAgency, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='drawings',
        to_field='agency_code',
    )
    source_reference        = models.CharField(max_length=200, blank=True)
    supersedes_drawing      = models.CharField(max_length=100, blank=True)
    superseded_by           = models.CharField(max_length=100, blank=True)

    # --- Physical Attributes ---
    sheet_size              = models.CharField(
        max_length=10, choices=SheetSize.choices, blank=True
    )
    scale                   = models.CharField(max_length=20, blank=True)
    number_of_sheets        = models.PositiveSmallIntegerField(default=1)

    # --- Quality ---
    drawing_readable        = models.CharField(
        max_length=20, choices=ReadabilityStatus.choices,
        default=ReadabilityStatus.READABLE
    )
    readability_remarks     = models.TextField(blank=True)

    # --- File Storage ---
    file_path               = models.CharField(max_length=500, blank=True)
    file_name               = models.CharField(max_length=200, blank=True)
    file_size               = models.BigIntegerField(null=True, blank=True)
    file_hash               = models.CharField(max_length=64, blank=True, db_index=True)
    mime_type               = models.CharField(max_length=50, blank=True)
    thumbnail_path          = models.CharField(max_length=500, blank=True)

    # --- OCR ---
    ocr_text                = models.TextField(blank=True)
    ocr_status              = models.CharField(
        max_length=20,
        choices=[('PENDING','Pending'),('COMPLETED','Completed'),('FAILED','Failed')],
        default='PENDING'
    )

    # --- Lifecycle ---
    is_latest               = models.BooleanField(default=True)
    is_active               = models.BooleanField(default=True)
    created_by              = models.ForeignKey(
        AUTH_USER, null=True, on_delete=models.SET_NULL,
        related_name='drawings_created', db_column='created_by_id',
    )
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_by              = models.ForeignKey(
        AUTH_USER, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='drawings_updated', db_column='updated_by_id',
    )
    updated_at              = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pl_drawing_master'
        ordering = ['drawing_number']
        indexes  = [
            models.Index(fields=['controlling_agency']),
            models.Index(fields=['drawing_type']),
            models.Index(fields=['drawing_readable']),
        ]

    def __str__(self):
        return f"{self.drawing_number} (Alt {self.current_alteration})"


# ---------------------------------------------------------------------------
# Specification Master
# ---------------------------------------------------------------------------
class SpecificationMaster(models.Model):

    class SpecType(models.TextChoices):
        MS = 'MS', 'Material Specification'
        PS = 'PS', 'Process Specification'
        TS = 'TS', 'Technical Specification'
        QS = 'QS', 'Quality Specification'
        ES = 'ES', 'Electrical Specification'
        IS = 'IS', 'Installation Specification'
        CS = 'CS', 'Coating Specification'
        WS = 'WS', 'Welding Specification'
        HS = 'HS', 'Heat Treatment Specification'
        NS = 'NS', 'NDT Specification'
        AS = 'AS', 'Assembly Specification'
        FS = 'FS', 'Functional Specification'

    spec_number             = models.CharField(max_length=100, unique=True, db_index=True)
    spec_title              = models.CharField(max_length=500)
    spec_type               = models.CharField(
        max_length=20, choices=SpecType.choices, blank=True
    )

    # --- Alteration ---
    current_alteration      = models.CharField(max_length=20, blank=True)
    alteration_date         = models.DateField(null=True, blank=True)
    alteration_description  = models.TextField(blank=True)
    probable_impacts        = models.TextField(blank=True)

    # --- Source ---
    controlling_agency      = models.ForeignKey(
        ControllingAgency, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='specifications',
        to_field='agency_code',
    )
    source_reference        = models.CharField(max_length=200, blank=True)
    supersedes_spec         = models.CharField(max_length=100, blank=True)
    superseded_by           = models.CharField(max_length=100, blank=True)

    # --- File Storage ---
    file_path               = models.CharField(max_length=500, blank=True)
    file_name               = models.CharField(max_length=200, blank=True)
    file_size               = models.BigIntegerField(null=True, blank=True)
    file_hash               = models.CharField(max_length=64, blank=True, db_index=True)

    # --- Lifecycle ---
    is_latest               = models.BooleanField(default=True)
    is_active               = models.BooleanField(default=True)
    created_by              = models.ForeignKey(
        AUTH_USER, null=True, on_delete=models.SET_NULL,
        related_name='specs_created', db_column='created_by_id',
    )
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_by              = models.ForeignKey(
        AUTH_USER, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='specs_updated', db_column='updated_by_id',
    )
    updated_at              = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pl_specification_master'
        ordering = ['spec_number']

    def __str__(self):
        return f"{self.spec_number} (Alt {self.current_alteration})"


# ---------------------------------------------------------------------------
# Vendor Drawing
# ---------------------------------------------------------------------------
class VendorDrawing(models.Model):

    class ApprovalStatus(models.TextChoices):
        PENDING  = 'PENDING',  'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    vendor_drawing_number   = models.CharField(max_length=100, db_index=True)
    vendor_drawing_title    = models.CharField(max_length=500)
    vendor_code             = models.CharField(max_length=50, blank=True)
    vendor_name             = models.CharField(max_length=200, blank=True)
    linked_pl_number        = models.ForeignKey(
        PLMaster, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='vendor_drawings',
        to_field='pl_number',
    )
    linked_clw_drawing      = models.CharField(
        max_length=100, blank=True,
        help_text='Corresponding CLW/OEM drawing number'
    )
    current_revision        = models.CharField(max_length=20, blank=True)
    revision_date           = models.DateField(null=True, blank=True)
    approval_status         = models.CharField(
        max_length=20, choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING
    )
    approval_date           = models.DateField(null=True, blank=True)
    approved_by             = models.ForeignKey(
        AUTH_USER, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='approved_vendor_drawings',
    )
    file_path               = models.CharField(max_length=500, blank=True)
    file_hash               = models.CharField(max_length=64, blank=True)
    is_latest               = models.BooleanField(default=True)
    is_active               = models.BooleanField(default=True)
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pl_vendor_drawing'
        ordering = ['vendor_drawing_number']
        unique_together = [('vendor_drawing_number', 'current_revision')]

    def __str__(self):
        return f"{self.vendor_drawing_number} — {self.vendor_name}"


# ---------------------------------------------------------------------------
# STR Master (Stores Type Register)
# ---------------------------------------------------------------------------
class STRMaster(models.Model):
    str_number          = models.CharField(max_length=50, unique=True, db_index=True)
    str_description     = models.TextField(blank=True)
    linked_pl_number    = models.ForeignKey(
        PLMaster, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='str_entries',
        to_field='pl_number',
    )
    unit_of_measure     = models.CharField(max_length=20, blank=True)
    stock_category      = models.CharField(max_length=20, blank=True)
    is_active           = models.BooleanField(default=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pl_str_master'
        ordering = ['str_number']

    def __str__(self):
        return self.str_number


# ---------------------------------------------------------------------------
# RDSO Reference
# ---------------------------------------------------------------------------
class RDSOReference(models.Model):

    class DocType(models.TextChoices):
        MS      = 'MS',      'Material Specification'
        SMI     = 'SMI',     'Special Maintenance Instruction'
        SPEC    = 'SPEC',    'Specification'
        STD_DRG = 'STD_DRG', 'Standard Drawing'
        MP      = 'MP',      'Modification Proposal'

    rdso_doc_type       = models.CharField(max_length=20, choices=DocType.choices)
    rdso_doc_number     = models.CharField(max_length=100, unique=True, db_index=True)
    rdso_doc_title      = models.CharField(max_length=500)
    current_revision    = models.CharField(max_length=20, blank=True)
    revision_date       = models.DateField(null=True, blank=True)
    effective_date      = models.DateField(null=True, blank=True)
    linked_pl_numbers   = models.JSONField(default=list, blank=True)
    applicability       = models.TextField(blank=True)
    file_path           = models.CharField(max_length=500, blank=True)
    file_hash           = models.CharField(max_length=64, blank=True)
    is_active           = models.BooleanField(default=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pl_rdso_reference'
        ordering = ['rdso_doc_number']

    def __str__(self):
        return f"{self.rdso_doc_number} (Rev {self.current_revision})"


# ---------------------------------------------------------------------------
# Alteration History — unified across DRAWING / SPEC / SMI / RDSO
# ---------------------------------------------------------------------------
class AlterationHistory(models.Model):

    class DocumentType(models.TextChoices):
        DRAWING = 'DRAWING', 'Drawing'
        SPEC    = 'SPEC',    'Specification'
        SMI     = 'SMI',     'SMI'
        RDSO    = 'RDSO',    'RDSO Reference'

    class ImplementationStatus(models.TextChoices):
        PENDING     = 'PENDING',     'Pending'
        IMPLEMENTED = 'IMPLEMENTED', 'Implemented'
        NA          = 'NA',          'Not Applicable'

    document_type           = models.CharField(
        max_length=20, choices=DocumentType.choices
    )
    document_number         = models.CharField(max_length=100, db_index=True)
    alteration_number       = models.CharField(max_length=20)
    previous_alteration     = models.CharField(max_length=20, blank=True)
    alteration_date         = models.DateField(null=True, blank=True)
    changes_description     = models.TextField(blank=True)
    change_reason           = models.TextField(blank=True)
    probable_impacts        = models.TextField(blank=True)
    source_agency           = models.CharField(max_length=10, blank=True)
    source_reference        = models.CharField(max_length=200, blank=True)
    source_date             = models.DateField(null=True, blank=True)
    affected_pl_numbers     = models.JSONField(default=list, blank=True)
    implementation_status   = models.CharField(
        max_length=20, choices=ImplementationStatus.choices,
        default=ImplementationStatus.PENDING
    )
    implemented_at_plw      = models.DateField(null=True, blank=True)
    implemented_by          = models.ForeignKey(
        AUTH_USER, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='alteration_implementations',
    )
    file_path_old           = models.CharField(max_length=500, blank=True)
    file_path_new           = models.CharField(max_length=500, blank=True)
    created_at              = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pl_alteration_history'
        ordering = ['-alteration_date', 'document_number']
        indexes  = [
            models.Index(fields=['document_type', 'document_number']),
            models.Index(fields=['implementation_status']),
        ]

    def __str__(self):
        return (
            f"{self.document_type}: {self.document_number} "
            f"Alt {self.alteration_number} [{self.implementation_status}]"
        )


# ---------------------------------------------------------------------------
# M2M Junction Tables — with metadata
# ---------------------------------------------------------------------------

class PLDrawingLink(models.Model):
    """M2M: PL ↔ Drawing"""
    pl_item     = models.ForeignKey(
        PLMaster, on_delete=models.CASCADE,
        related_name='drawing_links', to_field='pl_number',
    )
    drawing     = models.ForeignKey(
        DrawingMaster, on_delete=models.CASCADE,
        related_name='pl_links',
    )
    is_primary  = models.BooleanField(default=False)
    link_purpose = models.CharField(max_length=100, blank=True)
    remarks     = models.TextField(blank=True)
    linked_by   = models.ForeignKey(
        AUTH_USER, null=True, on_delete=models.SET_NULL,
        related_name='pl_drawing_links_created',
    )
    linked_at   = models.DateTimeField(auto_now_add=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table        = 'pl_drawing_link'
        unique_together = [('pl_item', 'drawing')]
        ordering        = ['-is_primary', 'drawing__drawing_number']

    def __str__(self):
        return f"{self.pl_item_id} ↔ {self.drawing.drawing_number}"


class PLSpecLink(models.Model):
    """M2M: PL ↔ Specification"""
    pl_item      = models.ForeignKey(
        PLMaster, on_delete=models.CASCADE,
        related_name='spec_links', to_field='pl_number',
    )
    specification = models.ForeignKey(
        SpecificationMaster, on_delete=models.CASCADE,
        related_name='pl_links',
    )
    is_primary   = models.BooleanField(default=False)
    link_purpose = models.CharField(max_length=100, blank=True)
    remarks      = models.TextField(blank=True)
    linked_by    = models.ForeignKey(
        AUTH_USER, null=True, on_delete=models.SET_NULL,
        related_name='pl_spec_links_created',
    )
    linked_at    = models.DateTimeField(auto_now_add=True)
    is_active    = models.BooleanField(default=True)

    class Meta:
        db_table        = 'pl_spec_link'
        unique_together = [('pl_item', 'specification')]
        ordering        = ['-is_primary', 'specification__spec_number']

    def __str__(self):
        return f"{self.pl_item_id} ↔ {self.specification.spec_number}"


class PLStandardLink(models.Model):
    """M2M: PL ↔ RDSO Reference / Standard"""
    pl_item       = models.ForeignKey(
        PLMaster, on_delete=models.CASCADE,
        related_name='standard_links', to_field='pl_number',
    )
    rdso_reference = models.ForeignKey(
        RDSOReference, on_delete=models.CASCADE,
        related_name='pl_links',
    )
    is_primary    = models.BooleanField(default=False)
    link_purpose  = models.CharField(max_length=100, blank=True)
    remarks       = models.TextField(blank=True)
    linked_by     = models.ForeignKey(
        AUTH_USER, null=True, on_delete=models.SET_NULL,
        related_name='pl_standard_links_created',
    )
    linked_at     = models.DateTimeField(auto_now_add=True)
    is_active     = models.BooleanField(default=True)

    class Meta:
        db_table        = 'pl_standard_link'
        unique_together = [('pl_item', 'rdso_reference')]
        ordering        = ['-is_primary', 'rdso_reference__rdso_doc_number']

    def __str__(self):
        return f"{self.pl_item_id} ↔ {self.rdso_reference.rdso_doc_number}"


class PLSMILink(models.Model):
    """M2M: PL ↔ SMI (via AlterationHistory where document_type=SMI)"""

    class ImplementationStatus(models.TextChoices):
        PENDING     = 'PENDING',     'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        IMPLEMENTED = 'IMPLEMENTED', 'Implemented'
        NA          = 'NA',          'Not Applicable'

    pl_item              = models.ForeignKey(
        PLMaster, on_delete=models.CASCADE,
        related_name='smi_links', to_field='pl_number',
    )
    smi_number           = models.CharField(max_length=100, db_index=True)
    smi_title            = models.CharField(max_length=500, blank=True)
    smi_type             = models.CharField(
        max_length=20,
        choices=[
            ('DESIGN',      'Design SMI'),
            ('PROCESS',     'Process SMI'),
            ('MATERIAL',    'Material SMI'),
            ('QUALITY',     'Quality SMI'),
            ('MAINTENANCE', 'Maintenance SMI'),
            ('SAFETY',      'Safety SMI'),
        ],
        blank=True
    )
    is_mandatory         = models.BooleanField(default=True)
    deadline             = models.DateField(null=True, blank=True)
    implementation_status = models.CharField(
        max_length=20, choices=ImplementationStatus.choices,
        default=ImplementationStatus.PENDING
    )
    implementation_date  = models.DateField(null=True, blank=True)
    implemented_by       = models.ForeignKey(
        AUTH_USER, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='smi_implementations',
    )
    remarks              = models.TextField(blank=True)
    linked_by            = models.ForeignKey(
        AUTH_USER, null=True, on_delete=models.SET_NULL,
        related_name='pl_smi_links_created',
    )
    linked_at            = models.DateTimeField(auto_now_add=True)
    is_active            = models.BooleanField(default=True)

    class Meta:
        db_table        = 'pl_smi_link'
        unique_together = [('pl_item', 'smi_number')]
        ordering        = ['-is_mandatory', 'smi_number']

    def __str__(self):
        return f"{self.pl_item_id} ↔ SMI:{self.smi_number} [{self.implementation_status}]"


# ---------------------------------------------------------------------------
# PLAlternate — interchangeable PL numbers
# ---------------------------------------------------------------------------
class PLAlternate(models.Model):
    pl_item           = models.ForeignKey(
        PLMaster, on_delete=models.CASCADE,
        related_name='alternates', to_field='pl_number',
    )
    alternate_pl      = models.ForeignKey(
        PLMaster, on_delete=models.CASCADE,
        related_name='alternate_for', to_field='pl_number',
        db_column='alternate_pl_number',
    )
    interchangeable   = models.BooleanField(default=True)
    remarks           = models.TextField(blank=True)
    linked_by         = models.ForeignKey(
        AUTH_USER, null=True, on_delete=models.SET_NULL,
        related_name='pl_alternates_created',
    )
    linked_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'pl_alternate'
        unique_together = [('pl_item', 'alternate_pl')]

    def __str__(self):
        return f"{self.pl_item_id} ↔ alt:{self.alternate_pl_id}"


# ---------------------------------------------------------------------------
# PLLocoApplicability — per-loco-type applicability with additional data
# ---------------------------------------------------------------------------
class PLLocoApplicability(models.Model):
    pl_item         = models.ForeignKey(
        PLMaster, on_delete=models.CASCADE,
        related_name='loco_applicabilities', to_field='pl_number',
    )
    loco_type       = models.CharField(
        max_length=20,
        choices=[
            ('WAG9',  'WAG9'),
            ('WAP7',  'WAP7'),
            ('WAP5',  'WAP5'),
            ('WAG9H', 'WAG9H'),
            ('WAP4',  'WAP4'),
            ('MEMU',  'MEMU'),
            ('DEMU',  'DEMU'),
            ('OTHER', 'Other'),
        ]
    )
    assembly_group  = models.CharField(max_length=10, blank=True,
                                       help_text='CLW group code: 01-20')
    qty_per_loco    = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )
    remarks         = models.TextField(blank=True)

    class Meta:
        db_table        = 'pl_loco_applicability'
        unique_together = [('pl_item', 'loco_type')]
        ordering        = ['loco_type']

    def __str__(self):
        return f"{self.pl_item_id} | {self.loco_type}"
