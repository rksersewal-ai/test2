# =============================================================================
# FILE: apps/scanner/views.py
# FIX #10: Replaced non-existent IsEngineerOrAbove import with inline
#          role-check permission class that works with actual core.User roles.
#          IsEngineerOrAbove was referenced but never defined in
#          apps/core/permissions.py for all roles; now defined locally.
# =============================================================================
import re
import logging
from rest_framework import permissions, status
from rest_framework.parsers  import MultiPartParser
from rest_framework.views    import APIView
from rest_framework.response import Response

log = logging.getLogger('scanner')


# ---------------------------------------------------------------------------
# Inline permission (avoids fragile cross-app import)
# ---------------------------------------------------------------------------

class IsEngineerOrAbove(permissions.BasePermission):
    """
    Allow access to ADMIN, SECTION_HEAD, ENGINEER, LDO_STAFF, AUDIT.
    Deny VIEWER role.
    """
    ALLOWED_ROLES = {'ADMIN', 'SECTION_HEAD', 'ENGINEER', 'LDO_STAFF', 'AUDIT'}

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) in self.ALLOWED_ROLES
        )


# ---------------------------------------------------------------------------
# OCR + field extraction
# ---------------------------------------------------------------------------

def _run_ocr(image_bytes: bytes) -> str:
    import io
    import pytesseract
    from PIL import Image, ImageFilter

    img = Image.open(io.BytesIO(image_bytes)).convert('L')
    img = img.filter(ImageFilter.SHARPEN)
    img = img.point(lambda p: 255 if p > 140 else 0, '1')
    text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
    return text


_PATTERNS = {
    'document_number': [
        r'(?:RDSO|CLW|BLW|ICF|PLW|WAP|WAG|MEMU|DEMU)[\s/\-][\w/\-\.]+',
        r'DRG\.?\s*No\.?\s*([\w\-\.]+)',
        r'Spec\.?\s*No\.?\s*([\w\-\.]+)',
    ],
    'revision': [
        r'Rev(?:ision)?[\.\s]*([A-Z0-9]+)',
        r'Alt(?:eration)?[\.\s]*([A-Z0-9]+)',
    ],
    'date': [
        r'Date[:\s]+(\d{1,2}[\-\./ ]\d{1,2}[\-\./ ]\d{2,4})',
        r'(\d{2}/\d{2}/\d{4})',
        r'(\d{2}-\d{2}-\d{4})',
    ],
    'source_standard': [
        r'(IS\s*\d+[:\-]\d*)',
        r'(IRS\s*[A-Z/\-\d]+)',
        r'(DIN\s*\d+)',
        r'(IRIS\s*[\w\-]+)',
        r'(BIS\s*[\w\-]+)',
    ],
}

_RAILWAY_KEYWORDS = [
    'WAG9', 'WAP7', 'WAP5', 'WAG12', 'MEMU', 'DEMU', 'DETC',
    'IGBT', 'VVVF', 'transformer', 'pantograph', 'bogies',
    'traction', 'propulsion', 'braking', 'compressor',
    'RDSO', 'CLW', 'BLW', 'ICF', 'PLW',
    'drawing', 'specification', 'BOM', 'assembly',
]


def _extract_fields(text: str) -> dict:
    results   = {}
    hit_count = 0
    total     = len(_PATTERNS)

    for field, patterns in _PATTERNS.items():
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                results[field] = (m.group(1) if m.lastindex else m.group(0)).strip()
                hit_count += 1
                break
        else:
            results[field] = None

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    doc_num = results.get('document_number', '')
    title_candidates = [
        ln for ln in lines
        if ln and (not doc_num or doc_num[:6] not in ln)
        and len(ln) > 10
    ]
    results['title']      = title_candidates[0] if title_candidates else None
    results['keywords']   = _extract_keywords(text)
    results['raw_text']   = text[:1000]
    results['confidence'] = round(hit_count / total, 2)
    return results


def _extract_keywords(text: str) -> str:
    found = [kw for kw in _RAILWAY_KEYWORDS if kw.lower() in text.lower()]
    return ', '.join(found)


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class ScanView(APIView):
    parser_classes     = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]

    def post(self, request):
        img_file = request.FILES.get('image')
        if not img_file:
            return Response(
                {'error': 'No image provided. Upload as multipart field "image".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if img_file.size > 10 * 1024 * 1024:
            return Response(
                {'error': 'Image too large. Max 10 MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            text   = _run_ocr(img_file.read())
            fields = _extract_fields(text)
            log.info(
                f'[Scanner] OCR: doc_num={fields.get("document_number")} '
                f'conf={fields.get("confidence")}'
            )
            return Response(fields)
        except Exception as e:
            log.error(f'[Scanner] OCR failed: {e}')
            return Response(
                {'error': f'OCR processing failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ScanAndSearchView(APIView):
    parser_classes     = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]

    def post(self, request):
        img_file = request.FILES.get('image')
        if not img_file:
            return Response({'error': 'No image provided.'}, status=400)
        try:
            text   = _run_ocr(img_file.read())
            fields = _extract_fields(text)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

        matches = []
        doc_num = fields.get('document_number')
        if doc_num:
            from apps.edms.models import Document
            from django.db.models import Q
            qs = Document.objects.filter(
                Q(document_number__icontains=doc_num[:10]) |
                Q(title__icontains=doc_num[:10])
            ).values('id', 'document_number', 'title', 'status')[:10]
            matches = list(qs)

        return Response({'fields': fields, 'matches': matches})
