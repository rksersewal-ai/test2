# =============================================================================
# FILE: apps/pl_master/serializers.py
# =============================================================================
from rest_framework import serializers
from .models import (
    ControllingAgency, PLMaster, DrawingMaster, SpecificationMaster,
    VendorDrawing, STRMaster, RDSOReference, AlterationHistory,
    PLDrawingLink, PLSpecLink, PLStandardLink, PLSMILink,
    PLAlternate, PLLocoApplicability,
)


# ── Controlling Agency ──────────────────────────────────────────────────────
class ControllingAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model  = ControllingAgency
        fields = '__all__'


# ── Loco Applicability ──────────────────────────────────────────────────────
class PLLocoApplicabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model  = PLLocoApplicability
        fields = ['loco_type', 'assembly_group', 'qty_per_loco', 'remarks']


# ── Alternate PL ────────────────────────────────────────────────────────────
class PLAlternateSerializer(serializers.ModelSerializer):
    alternate_pl_number = serializers.CharField(source='alternate_pl.pl_number', read_only=True)
    alternate_description = serializers.CharField(
        source='alternate_pl.part_description', read_only=True
    )

    class Meta:
        model  = PLAlternate
        fields = ['alternate_pl_number', 'alternate_description', 'interchangeable', 'remarks']


# ── Drawing Link ────────────────────────────────────────────────────────────
class PLDrawingLinkReadSerializer(serializers.ModelSerializer):
    drawing_number = serializers.CharField(source='drawing.drawing_number', read_only=True)
    drawing_title  = serializers.CharField(source='drawing.drawing_title',  read_only=True)
    drawing_type   = serializers.CharField(source='drawing.drawing_type',   read_only=True)
    current_alteration = serializers.CharField(
        source='drawing.current_alteration', read_only=True
    )

    class Meta:
        model  = PLDrawingLink
        fields = [
            'id', 'drawing_number', 'drawing_title', 'drawing_type',
            'current_alteration', 'is_primary', 'link_purpose', 'remarks', 'linked_at',
        ]


class PLDrawingLinkWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PLDrawingLink
        fields = ['pl_item', 'drawing', 'is_primary', 'link_purpose', 'remarks']


# ── Spec Link ────────────────────────────────────────────────────────────────
class PLSpecLinkReadSerializer(serializers.ModelSerializer):
    spec_number        = serializers.CharField(source='specification.spec_number',  read_only=True)
    spec_title         = serializers.CharField(source='specification.spec_title',   read_only=True)
    spec_type          = serializers.CharField(source='specification.spec_type',    read_only=True)
    current_alteration = serializers.CharField(
        source='specification.current_alteration', read_only=True
    )

    class Meta:
        model  = PLSpecLink
        fields = [
            'id', 'spec_number', 'spec_title', 'spec_type',
            'current_alteration', 'is_primary', 'link_purpose', 'remarks', 'linked_at',
        ]


class PLSpecLinkWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PLSpecLink
        fields = ['pl_item', 'specification', 'is_primary', 'link_purpose', 'remarks']


# ── Standard Link ────────────────────────────────────────────────────────────
class PLStandardLinkReadSerializer(serializers.ModelSerializer):
    rdso_doc_number = serializers.CharField(
        source='rdso_reference.rdso_doc_number', read_only=True
    )
    rdso_doc_title  = serializers.CharField(
        source='rdso_reference.rdso_doc_title',  read_only=True
    )
    rdso_doc_type   = serializers.CharField(
        source='rdso_reference.rdso_doc_type',   read_only=True
    )

    class Meta:
        model  = PLStandardLink
        fields = [
            'id', 'rdso_doc_number', 'rdso_doc_title', 'rdso_doc_type',
            'is_primary', 'link_purpose', 'remarks', 'linked_at',
        ]


class PLStandardLinkWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PLStandardLink
        fields = ['pl_item', 'rdso_reference', 'is_primary', 'link_purpose', 'remarks']


# ── SMI Link ────────────────────────────────────────────────────────────────
class PLSMILinkReadSerializer(serializers.ModelSerializer):
    implemented_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = PLSMILink
        fields = [
            'id', 'smi_number', 'smi_title', 'smi_type',
            'is_mandatory', 'deadline', 'implementation_status',
            'implementation_date', 'implemented_by_name', 'remarks', 'linked_at',
        ]

    def get_implemented_by_name(self, obj):
        return obj.implemented_by.full_name if obj.implemented_by else None


class PLSMILinkWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PLSMILink
        fields = [
            'pl_item', 'smi_number', 'smi_title', 'smi_type',
            'is_mandatory', 'deadline', 'implementation_status',
            'implementation_date', 'implemented_by', 'remarks',
        ]


# ── PLMaster List (compact) ─────────────────────────────────────────────────
class PLMasterListSerializer(serializers.ModelSerializer):
    controlling_agency_code = serializers.CharField(
        source='controlling_agency.agency_code', read_only=True, default=''
    )
    description = serializers.CharField(source='part_description', read_only=True)
    loco_types = serializers.SerializerMethodField()
    controlling_agency_name = serializers.CharField(
        source='controlling_agency.agency_name', read_only=True, default=''
    )

    def get_loco_types(self, obj):
        return obj.used_in or []

    class Meta:
        model  = PLMaster
        fields = [
            'pl_number', 'part_description', 'description', 'inspection_category',
            'safety_item', 'safety_classification', 'vd_item', 'nvd_item',
            'controlling_agency_code', 'controlling_agency_name', 'uvam_id', 'used_in', 'loco_types',
            'application_area', 'is_active',
        ]


# ── PLMaster Detail (full) ──────────────────────────────────────────────────
class PLMasterDetailSerializer(serializers.ModelSerializer):
    controlling_agency_code = serializers.CharField(
        source='controlling_agency.agency_code', read_only=True, default=''
    )
    mother_part_description_resolved = serializers.CharField(
        source='mother_part.part_description', read_only=True, default=''
    )
    design_supervisor_name    = serializers.SerializerMethodField()
    concerned_supervisor_name = serializers.SerializerMethodField()

    drawing_links  = PLDrawingLinkReadSerializer(many=True, read_only=True)
    spec_links     = PLSpecLinkReadSerializer(many=True, read_only=True)
    standard_links = PLStandardLinkReadSerializer(many=True, read_only=True)
    smi_links      = PLSMILinkReadSerializer(many=True, read_only=True)
    alternates     = PLAlternateSerializer(many=True, read_only=True)
    loco_applicabilities = PLLocoApplicabilitySerializer(many=True, read_only=True)
    description = serializers.CharField(source='part_description', read_only=True)
    loco_types = serializers.SerializerMethodField()
    controlling_agency_name = serializers.CharField(
        source='controlling_agency.agency_name', read_only=True, default=''
    )

    class Meta:
        model  = PLMaster
        fields = '__all__'

    def get_loco_types(self, obj):
        return obj.used_in or []

    def get_design_supervisor_name(self, obj):
        return obj.design_supervisor_id.full_name if obj.design_supervisor_id else obj.design_supervisor

    def get_concerned_supervisor_name(self, obj):
        return obj.concerned_supervisor_id.full_name if obj.concerned_supervisor_id else obj.concerned_supervisor


# ── PLMaster Write ──────────────────────────────────────────────────────────
class PLMasterWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PLMaster
        fields = [
            'pl_number', 'part_description', 'part_description_hindi',
            'mother_part', 'mother_part_description',
            'safety_item', 'safety_classification', 'severity_of_failure',
            'consequences_upon_failure', 'failure_mode',
            'functionality', 'used_in', 'application_area',
            'inspection_category', 'stage_inspection_reqd', 'inspection_agency',
            'controlling_agency', 'controlling_pu', 'rdso_controlled',
            'vd_item', 'uvam_id', 'uvam_category', 'nvd_item',
            'set_list_number', 'set_list_description',
            'design_supervisor', 'design_supervisor_id',
            'concerned_supervisor', 'concerned_supervisor_id',
            'e_office_file_no', 'case_no',
            'keywords', 'tags', 'remarks', 'is_active',
        ]

    def validate(self, data):
        if data.get('safety_item') and not data.get('safety_classification'):
            raise serializers.ValidationError(
                {'safety_classification': 'Required when safety_item is True.'}
            )
        return data


# ── Drawing Master ───────────────────────────────────────────────────────────
class DrawingMasterListSerializer(serializers.ModelSerializer):
    drawing_id = serializers.IntegerField(source='id', read_only=True)
    controlling_agency_name = serializers.CharField(
        source='controlling_agency.agency_name', read_only=True, default=''
    )

    class Meta:
        model  = DrawingMaster
        fields = [
            'drawing_id', 'drawing_number', 'drawing_title', 'drawing_type',
            'current_alteration', 'alteration_date', 'controlling_agency',
            'controlling_agency_name',
            'drawing_readable', 'sheet_size', 'is_latest', 'is_active',
        ]


class DrawingMasterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DrawingMaster
        fields = '__all__'


class DrawingMasterWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DrawingMaster
        exclude = ['created_at', 'updated_at', 'created_by', 'updated_by']


# ── Specification Master ─────────────────────────────────────────────────────
class SpecificationMasterListSerializer(serializers.ModelSerializer):
    spec_id = serializers.IntegerField(source='id', read_only=True)
    controlling_agency_name = serializers.CharField(
        source='controlling_agency.agency_name', read_only=True, default=''
    )

    class Meta:
        model  = SpecificationMaster
        fields = [
            'spec_id', 'spec_number', 'spec_title', 'spec_type',
            'current_alteration', 'alteration_date', 'controlling_agency',
            'controlling_agency_name',
            'is_latest', 'is_active',
        ]


class SpecificationMasterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SpecificationMaster
        fields = '__all__'


class SpecificationMasterWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SpecificationMaster
        exclude = ['created_at', 'updated_at', 'created_by', 'updated_by']


# ── Vendor Drawing ───────────────────────────────────────────────────────────
class VendorDrawingSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = VendorDrawing
        fields = '__all__'

    def get_approved_by_name(self, obj):
        return obj.approved_by.full_name if obj.approved_by else None


# ── STR Master ───────────────────────────────────────────────────────────────
class STRMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model  = STRMaster
        fields = '__all__'


# ── RDSO Reference ───────────────────────────────────────────────────────────
class RDSORefListSerializer(serializers.ModelSerializer):
    rdso_ref_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model  = RDSOReference
        fields = [
            'rdso_ref_id', 'rdso_doc_type', 'rdso_doc_number', 'rdso_doc_title',
            'current_revision', 'revision_date', 'effective_date', 'is_active',
        ]


class RDSORefDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RDSOReference
        fields = '__all__'


# ── Alteration History ───────────────────────────────────────────────────────
class AlterationHistorySerializer(serializers.ModelSerializer):
    implemented_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = AlterationHistory
        fields = '__all__'

    def get_implemented_by_name(self, obj):
        return obj.implemented_by.full_name if obj.implemented_by else None
