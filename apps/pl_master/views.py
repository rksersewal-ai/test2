# =============================================================================
# FILE: apps/pl_master/views.py
# =============================================================================
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import (
    CanCreateWorkEntry, CanEditWorkEntry, ENGINEER_AND_ABOVE, OFFICER_AND_ABOVE,
    get_user_role,
)
from .models import (
    ControllingAgency, PLMaster, DrawingMaster, SpecificationMaster,
    VendorDrawing, STRMaster, RDSOReference, AlterationHistory,
    PLDrawingLink, PLSpecLink, PLStandardLink, PLSMILink,
    PLAlternate, PLLocoApplicability,
)
from .repositories import (
    DEFAULT_PAGE_SIZE,
    _safe_int,
    search_pl_master, get_pl_detail, get_bom_tree,
    search_drawings, search_specifications,
    get_alteration_history, search_vendor_drawings,
)
from .serializers import (
    ControllingAgencySerializer,
    PLMasterListSerializer, PLMasterDetailSerializer, PLMasterWriteSerializer,
    DrawingMasterListSerializer, DrawingMasterDetailSerializer, DrawingMasterWriteSerializer,
    SpecificationMasterListSerializer, SpecificationMasterDetailSerializer,
    SpecificationMasterWriteSerializer,
    VendorDrawingSerializer,
    STRMasterSerializer,
    RDSORefListSerializer, RDSORefDetailSerializer,
    AlterationHistorySerializer,
    PLDrawingLinkWriteSerializer, PLSpecLinkWriteSerializer,
    PLStandardLinkWriteSerializer, PLSMILinkWriteSerializer,
    PLSMILinkReadSerializer,
)


def _is_officer_or_above(request):
    return get_user_role(request) in OFFICER_AND_ABOVE


def _is_engineer_or_above(request):
    return get_user_role(request) in ENGINEER_AND_ABOVE


# ── Controlling Agency ───────────────────────────────────────────────────────
class ControllingAgencyListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ControllingAgency.objects.filter(is_active=True)
        return Response(ControllingAgencySerializer(qs, many=True).data)

    def post(self, request):
        if not _is_officer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = ControllingAgencySerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


# ── PL Master ────────────────────────────────────────────────────────────────
class PLMasterListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        p = request.query_params
        result = search_pl_master(
            q                    = p.get('q'),
            inspection_category  = p.get('inspection_category'),
            safety_item          = {'true': True, 'false': False}.get(
                                       p.get('safety_item', '').lower()),
            vd_item              = {'true': True, 'false': False}.get(
                                       p.get('vd_item', '').lower()),
            nvd_item             = {'true': True, 'false': False}.get(
                                       p.get('nvd_item', '').lower()),
            controlling_agency   = p.get('controlling_agency'),
            used_in              = p.get('used_in'),
            uvam_id              = p.get('uvam_id'),
            application_area     = p.get('application_area'),
            is_active            = p.get('is_active', 'true').lower() != 'false',
            page                 = _safe_int(p.get('page'), 1),
            page_size            = _safe_int(p.get('page_size'), DEFAULT_PAGE_SIZE),
        )
        result['results'] = PLMasterListSerializer(
            result['results'], many=True
        ).data
        return Response(result)

    def post(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = PLMasterWriteSerializer(data=request.data)
        if s.is_valid():
            obj = s.save(
                created_by=request.user,
                updated_by=request.user,
            )
            return Response(
                PLMasterDetailSerializer(get_pl_detail(obj.pl_number)).data,
                status=201,
            )
        return Response(s.errors, status=400)


class PLMasterDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, pl_number):
        obj = get_pl_detail(pl_number)
        if not obj:
            return None
        return obj

    def get(self, request, pl_number):
        obj = self._get(pl_number)
        if not obj:
            return Response({'detail': 'Not found.'}, status=404)
        return Response(PLMasterDetailSerializer(obj).data)

    def patch(self, request, pl_number):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        try:
            obj = PLMaster.objects.get(pl_number=pl_number)
        except PLMaster.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        s = PLMasterWriteSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            updated = s.save(updated_by=request.user)
            return Response(PLMasterDetailSerializer(get_pl_detail(updated.pl_number)).data)
        return Response(s.errors, status=400)

    def delete(self, request, pl_number):
        if not _is_officer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        try:
            obj = PLMaster.objects.get(pl_number=pl_number)
        except PLMaster.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        obj.is_active = False
        obj.updated_by = request.user
        obj.save(update_fields=['is_active', 'updated_by', 'updated_at'])
        return Response(status=204)


class PLBOMTreeView(APIView):
    """GET /api/v1/pl-master/<pl_number>/bom/ — recursive BOM tree."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pl_number):
        max_depth = _safe_int(request.query_params.get('max_depth'), 5)
        tree = get_bom_tree(pl_number, max_depth=max_depth)
        return Response({'pl_number': pl_number, 'children': tree})


# ── Drawing Master ───────────────────────────────────────────────────────────
class DrawingMasterListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        p = request.query_params
        result = search_drawings(
            q                  = p.get('q'),
            drawing_type       = p.get('drawing_type'),
            controlling_agency = p.get('controlling_agency'),
            drawing_readable   = p.get('drawing_readable'),
            is_active          = p.get('is_active', 'true').lower() != 'false',
            page               = _safe_int(p.get('page'), 1),
            page_size          = _safe_int(p.get('page_size'), DEFAULT_PAGE_SIZE),
        )
        result['results'] = DrawingMasterListSerializer(
            result['results'], many=True
        ).data
        return Response(result)

    def post(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = DrawingMasterWriteSerializer(data=request.data)
        if s.is_valid():
            obj = s.save(created_by=request.user, updated_by=request.user)
            return Response(DrawingMasterDetailSerializer(obj).data, status=201)
        return Response(s.errors, status=400)


class DrawingMasterDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, drawing_number):
        try:
            obj = DrawingMaster.objects.select_related('controlling_agency').get(
                drawing_number=drawing_number
            )
        except DrawingMaster.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        return Response(DrawingMasterDetailSerializer(obj).data)

    def patch(self, request, drawing_number):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        try:
            obj = DrawingMaster.objects.get(drawing_number=drawing_number)
        except DrawingMaster.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        s = DrawingMasterWriteSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            s.save(updated_by=request.user)
            return Response(DrawingMasterDetailSerializer(obj).data)
        return Response(s.errors, status=400)


# ── Specification Master ─────────────────────────────────────────────────────
class SpecMasterListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        p = request.query_params
        result = search_specifications(
            q                  = p.get('q'),
            spec_type          = p.get('spec_type'),
            controlling_agency = p.get('controlling_agency'),
            is_active          = p.get('is_active', 'true').lower() != 'false',
            page               = _safe_int(p.get('page'), 1),
            page_size          = _safe_int(p.get('page_size'), DEFAULT_PAGE_SIZE),
        )
        result['results'] = SpecificationMasterListSerializer(
            result['results'], many=True
        ).data
        return Response(result)

    def post(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = SpecificationMasterWriteSerializer(data=request.data)
        if s.is_valid():
            obj = s.save(created_by=request.user, updated_by=request.user)
            return Response(SpecificationMasterDetailSerializer(obj).data, status=201)
        return Response(s.errors, status=400)


class SpecMasterDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, spec_number):
        try:
            obj = SpecificationMaster.objects.select_related('controlling_agency').get(
                spec_number=spec_number
            )
        except SpecificationMaster.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        return Response(SpecificationMasterDetailSerializer(obj).data)

    def patch(self, request, spec_number):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        try:
            obj = SpecificationMaster.objects.get(spec_number=spec_number)
        except SpecificationMaster.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        s = SpecificationMasterWriteSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            s.save(updated_by=request.user)
            return Response(SpecificationMasterDetailSerializer(obj).data)
        return Response(s.errors, status=400)


# ── Vendor Drawings ──────────────────────────────────────────────────────────
class VendorDrawingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        p = request.query_params
        result = search_vendor_drawings(
            q               = p.get('q'),
            vendor_code     = p.get('vendor_code'),
            approval_status = p.get('approval_status'),
            pl_number       = p.get('pl_number'),
            page            = _safe_int(p.get('page'), 1),
            page_size       = _safe_int(p.get('page_size'), DEFAULT_PAGE_SIZE),
        )
        result['results'] = VendorDrawingSerializer(
            result['results'], many=True
        ).data
        return Response(result)

    def post(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = VendorDrawingSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


# ── STR Master ───────────────────────────────────────────────────────────────
class STRMasterListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q')
        pl = request.query_params.get('pl_number')
        qs = STRMaster.objects.filter(is_active=True)
        if q:
            qs = qs.filter(
                STRMaster.objects.model._default_manager
                .none().query.__class__()  # just use Q directly
            )
            from django.db.models import Q as _Q
            qs = STRMaster.objects.filter(is_active=True).filter(
                _Q(str_number__icontains=q) | _Q(str_description__icontains=q)
            )
        if pl:
            qs = qs.filter(linked_pl_number__pl_number=pl)
        return Response(STRMasterSerializer(qs[:200], many=True).data)

    def post(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = STRMasterSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


# ── RDSO References ──────────────────────────────────────────────────────────
class RDSORefListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        p = request.query_params
        from django.db.models import Q as _Q
        qs = RDSOReference.objects.filter(is_active=True)
        q = p.get('q')
        doc_type = p.get('doc_type')
        pl = p.get('pl_number')
        if q:
            qs = qs.filter(
                _Q(rdso_doc_number__icontains=q) | _Q(rdso_doc_title__icontains=q)
            )
        if doc_type:
            qs = qs.filter(rdso_doc_type=doc_type)
        if pl:
            qs = qs.filter(linked_pl_numbers__contains=[pl])
        page = _safe_int(p.get('page'), 1)
        page_size = _safe_int(p.get('page_size'), DEFAULT_PAGE_SIZE)
        total = qs.count()
        offset = (page - 1) * page_size
        results = RDSORefListSerializer(qs[offset:offset + page_size], many=True).data
        return Response({
            'results': results, 'total_count': total,
            'page': page, 'page_size': page_size,
        })

    def post(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = RDSORefDetailSerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


# ── Alteration History ───────────────────────────────────────────────────────
class AlterationHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        p = request.query_params
        result = get_alteration_history(
            document_type         = p.get('document_type'),
            document_number       = p.get('document_number'),
            implementation_status = p.get('implementation_status'),
            source_agency         = p.get('source_agency'),
            pl_number             = p.get('pl_number'),
            page                  = _safe_int(p.get('page'), 1),
            page_size             = _safe_int(p.get('page_size'), DEFAULT_PAGE_SIZE),
        )
        result['results'] = AlterationHistorySerializer(
            result['results'], many=True
        ).data
        return Response(result)

    def post(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = AlterationHistorySerializer(data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


# ── PL Document Links (M2M management) ──────────────────────────────────────
class PLDrawingLinkView(APIView):
    """POST to add, DELETE to remove a PL↔Drawing link."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = PLDrawingLinkWriteSerializer(data=request.data)
        if s.is_valid():
            s.save(linked_by=request.user)
            return Response(s.data, status=201)
        return Response(s.errors, status=400)

    def delete(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        pl = request.data.get('pl_item')
        drg = request.data.get('drawing')
        deleted, _ = PLDrawingLink.objects.filter(pl_item=pl, drawing=drg).delete()
        if not deleted:
            return Response({'detail': 'Link not found.'}, status=404)
        return Response(status=204)


class PLSpecLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = PLSpecLinkWriteSerializer(data=request.data)
        if s.is_valid():
            s.save(linked_by=request.user)
            return Response(s.data, status=201)
        return Response(s.errors, status=400)

    def delete(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        pl = request.data.get('pl_item')
        spec = request.data.get('specification')
        deleted, _ = PLSpecLink.objects.filter(pl_item=pl, specification=spec).delete()
        if not deleted:
            return Response({'detail': 'Link not found.'}, status=404)
        return Response(status=204)


class PLStandardLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = PLStandardLinkWriteSerializer(data=request.data)
        if s.is_valid():
            s.save(linked_by=request.user)
            return Response(s.data, status=201)
        return Response(s.errors, status=400)

    def delete(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        from .models import PLStandardLink as _L
        pl = request.data.get('pl_item')
        ref = request.data.get('rdso_reference')
        deleted, _ = _L.objects.filter(pl_item=pl, rdso_reference=ref).delete()
        if not deleted:
            return Response({'detail': 'Link not found.'}, status=404)
        return Response(status=204)


class PLSMILinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        s = PLSMILinkWriteSerializer(data=request.data)
        if s.is_valid():
            s.save(linked_by=request.user)
            return Response(
                PLSMILinkReadSerializer(s.instance).data, status=201
            )
        return Response(s.errors, status=400)

    def patch(self, request, pk):
        """Update SMI implementation status."""
        if not _is_engineer_or_above(request):
            return Response({'detail': 'Insufficient role.'}, status=403)
        from .models import PLSMILink as _L
        try:
            obj = _L.objects.get(pk=pk)
        except _L.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        s = PLSMILinkWriteSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            s.save()
            return Response(PLSMILinkReadSerializer(obj).data)
        return Response(s.errors, status=400)
