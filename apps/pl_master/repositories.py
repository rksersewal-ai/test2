# =============================================================================
# FILE: apps/pl_master/repositories.py
# All DB queries isolated here — views stay thin.
# =============================================================================
from __future__ import annotations
from django.db.models import Q, Prefetch
from .models import (
    PLMaster, DrawingMaster, SpecificationMaster,
    RDSOReference, AlterationHistory, VendorDrawing,
    PLDrawingLink, PLSpecLink, PLSMILink,
)

DEFAULT_PAGE_SIZE = 25


def _safe_int(val, default):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def _paginate(qs, page, page_size):
    total = qs.count()
    page_size = min(page_size, 500)
    page = max(page, 1)
    offset = (page - 1) * page_size
    return {
        'results':     list(qs[offset: offset + page_size]),
        'total_count': total,
        'page':        page,
        'page_size':   page_size,
        'total_pages': (total + page_size - 1) // page_size,
    }


# ── PL Master ────────────────────────────────────────────────────────────────

def search_pl_master(
    q=None,
    inspection_category=None,
    safety_item=None,
    vd_item=None,
    nvd_item=None,
    controlling_agency=None,
    used_in=None,
    uvam_id=None,
    application_area=None,
    is_active=True,
    page=1,
    page_size=DEFAULT_PAGE_SIZE,
):
    qs = PLMaster.objects.select_related(
        'controlling_agency', 'design_supervisor_id', 'concerned_supervisor_id'
    )
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if q:
        qs = qs.filter(
            Q(pl_number__icontains=q)
            | Q(part_description__icontains=q)
            | Q(part_description_hindi__icontains=q)
            | Q(functionality__icontains=q)
            | Q(keywords__contains=[q])
        )
    if inspection_category:
        qs = qs.filter(inspection_category=inspection_category)
    if safety_item is not None:
        qs = qs.filter(safety_item=safety_item)
    if vd_item is not None:
        qs = qs.filter(vd_item=vd_item)
    if nvd_item is not None:
        qs = qs.filter(nvd_item=nvd_item)
    if controlling_agency:
        qs = qs.filter(controlling_agency__agency_code=controlling_agency)
    if used_in:
        qs = qs.filter(used_in__contains=[used_in])
    if uvam_id:
        qs = qs.filter(uvam_id__icontains=uvam_id)
    if application_area:
        qs = qs.filter(application_area__icontains=application_area)
    return _paginate(qs.order_by('pl_number'), page, page_size)


def get_pl_detail(pl_number: str):
    try:
        return (
            PLMaster.objects
            .select_related(
                'controlling_agency',
                'design_supervisor_id',
                'concerned_supervisor_id',
                'mother_part',
            )
            .prefetch_related(
                Prefetch('drawing_links',
                         queryset=PLDrawingLink.objects.select_related('drawing').filter(is_active=True)),
                Prefetch('spec_links',
                         queryset=PLSpecLink.objects.select_related('specification').filter(is_active=True)),
                'standard_links__rdso_reference',
                Prefetch('smi_links',
                         queryset=PLSMILink.objects.filter(is_active=True)),
                'alternates__alternate_pl',
                'loco_applicabilities',
            )
            .get(pl_number=pl_number)
        )
    except PLMaster.DoesNotExist:
        return None


def get_bom_children(pl_number: str):
    """Direct child parts (one level deep)."""
    return PLMaster.objects.filter(
        mother_part__pl_number=pl_number, is_active=True
    ).order_by('pl_number')


def get_bom_tree(pl_number: str, depth: int = 0, max_depth: int = 5):
    """Recursive BOM tree — returns nested dict."""
    if depth >= max_depth:
        return []
    children = get_bom_children(pl_number)
    return [
        {
            'pl_number':        c.pl_number,
            'part_description': c.part_description,
            'inspection_category': c.inspection_category,
            'children': get_bom_tree(c.pl_number, depth + 1, max_depth),
        }
        for c in children
    ]


# ── Drawing Master ───────────────────────────────────────────────────────────

def search_drawings(
    q=None, drawing_type=None, controlling_agency=None,
    drawing_readable=None, is_active=True,
    page=1, page_size=DEFAULT_PAGE_SIZE,
):
    qs = DrawingMaster.objects.select_related('controlling_agency')
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if q:
        qs = qs.filter(
            Q(drawing_number__icontains=q)
            | Q(drawing_title__icontains=q)
            | Q(ocr_text__icontains=q)
        )
    if drawing_type:
        qs = qs.filter(drawing_type=drawing_type)
    if controlling_agency:
        qs = qs.filter(controlling_agency__agency_code=controlling_agency)
    if drawing_readable:
        qs = qs.filter(drawing_readable=drawing_readable)
    return _paginate(qs.order_by('drawing_number'), page, page_size)


# ── Specification Master ─────────────────────────────────────────────────────

def search_specifications(
    q=None, spec_type=None, controlling_agency=None,
    is_active=True, page=1, page_size=DEFAULT_PAGE_SIZE,
):
    qs = SpecificationMaster.objects.select_related('controlling_agency')
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if q:
        qs = qs.filter(
            Q(spec_number__icontains=q)
            | Q(spec_title__icontains=q)
        )
    if spec_type:
        qs = qs.filter(spec_type=spec_type)
    if controlling_agency:
        qs = qs.filter(controlling_agency__agency_code=controlling_agency)
    return _paginate(qs.order_by('spec_number'), page, page_size)


# ── Alteration History ───────────────────────────────────────────────────────

def get_alteration_history(
    document_type=None, document_number=None,
    implementation_status=None, source_agency=None,
    pl_number=None,
    page=1, page_size=DEFAULT_PAGE_SIZE,
):
    qs = AlterationHistory.objects.select_related('implemented_by')
    if document_type:
        qs = qs.filter(document_type=document_type)
    if document_number:
        qs = qs.filter(document_number__icontains=document_number)
    if implementation_status:
        qs = qs.filter(implementation_status=implementation_status)
    if source_agency:
        qs = qs.filter(source_agency=source_agency)
    if pl_number:
        # filter records where pl_number is in the affected_pl_numbers array
        qs = qs.filter(affected_pl_numbers__contains=[pl_number])
    return _paginate(qs.order_by('-alteration_date'), page, page_size)


# ── Vendor Drawings ──────────────────────────────────────────────────────────

def search_vendor_drawings(
    q=None, vendor_code=None, approval_status=None,
    pl_number=None, page=1, page_size=DEFAULT_PAGE_SIZE,
):
    qs = VendorDrawing.objects.select_related('linked_pl_number', 'approved_by')
    if q:
        qs = qs.filter(
            Q(vendor_drawing_number__icontains=q)
            | Q(vendor_drawing_title__icontains=q)
            | Q(vendor_name__icontains=q)
        )
    if vendor_code:
        qs = qs.filter(vendor_code=vendor_code)
    if approval_status:
        qs = qs.filter(approval_status=approval_status)
    if pl_number:
        qs = qs.filter(linked_pl_number__pl_number=pl_number)
    return _paginate(qs.filter(is_active=True).order_by('vendor_drawing_number'), page, page_size)
