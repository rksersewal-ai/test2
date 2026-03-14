# =============================================================================
# FILE: apps/scanner/views.py
# SPRINT 8 — PWA Scanner OCR API
#
# POST /api/v1/scanner/scan/
#   Accepts: multipart image (JPEG/PNG) from mobile camera
#   Returns: extracted fields  {document_number, title, revision, date,
#                               source_standard, keywords, confidence}
#
# The backend runs Tesseract OCR on the uploaded image, then applies
# railway-domain regex patterns to extract structured metadata.
# The frontend auto-fills the New Document form with the results.
#
# POST /api/v1/scanner/scan-and-search/
#   Same OCR step, but also searches existing EDMS documents by document_number
#   and returns matches for "find existing" workflow.
# =============================================================================
import re
import logging
from pathlib import Path

from rest_framework import permissions, status
from rest_framework.parsers  import MultiPartParser
from rest_framework.views    import APIView
from rest_framework.response import Response

from apps.core.permissions import IsEngineerOrAbove

log = logging.getLogger('scanner')


# ---------------------------------------------------------------------------
# OCR + field extraction
# ---------------------------------------------------------------------------

def _run_ocr(image_bytes: bytes) -> str:
    """
    Run Tesseract OCR on image bytes.
    Returns raw text string.
    Preprocessing: convert to grayscale + threshold via Pillow for better accuracy.
    """
    import io
    import pytesseract
    from PIL import Image, ImageFilter

    img = Image.open(io.BytesIO(image_bytes)).convert('L')   # greyscale
    img = img.filter(ImageFilter.SHARPEN)
    # Binarise: helps with printed text on scanned covers
    img = img.point(lambda p: 255 if p > 140 else 0, '1')
    text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
    return text


# Pattern bank for Indian Railway document covers
_PATTERNS = {
    'document_number': [
        # RDSO / CLW / BLW style:  RDSO/2023/EL/0047,  CLW/M/ESS/0012
        r'(?:RDSO|CLW|BLW|ICF|PLW|WAP|WAG|MEMU|DEMU)[\s/\-][\w/\-\.]+',
        # Drawing number:  DRG No. WD-97017-S-01
        r'DRG\.?\s*No\.?\s*([\w\-\.]+)',
        # Spec number:  Spec. No. MP-0.0600.01
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


def _extract_fields(text: str) -> dict:
    """
    Extract structured fields from raw OCR text using regex pattern bank.
    Returns dict with best match per field + a confidence score (0–1).
    """
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

    # Extract title: first non-empty line that is not a document number
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    doc_num = results.get('document_number', '')
    title_candidates = [
        ln for ln in lines
        if ln and (not doc_num or doc_num[:6] not in ln)
        and len(ln) > 10
    ]
    results['title']      = title_candidates[0] if title_candidates else None
    results['keywords']   = _extract_keywords(text)
    results['raw_text']   = text[:1000]          # first 1k chars for debug
    results['confidence'] = round(hit_count / total, 2)
    return results


_RAILWAY_KEYWORDS = [
    'WAG9', 'WAP7', 'WAP5', 'WAG12', 'MEMU', 'DEMU', 'DETC',
    'IGBT', 'VVVF', 'transformer', 'pantograph', 'bogies',
    'traction', 'propulsion', 'braking', 'compressor',
    'RDSO', 'CLW', 'BLW', 'ICF', 'PLW',
    'drawing', 'specification', 'BOM', 'assembly',
]


def _extract_keywords(text: str) -> str:
    """Return comma-separated keywords found in the OCR text."""
    found = [
        kw for kw in _RAILWAY_KEYWORDS
        if kw.lower() in text.lower()
    ]
    return ', '.join(found)


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class ScanView(APIView):
    """
    POST /api/v1/scanner/scan/
    Accepts multipart: field name 'image'
    Returns extracted metadata fields.
    """
    parser_classes     = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated, IsEngineerOrAbove]

    def post(self, request):
        img_file = request.FILES.get('image')
        if not img_file:
            return Response(
                {'error': 'No image provided. Upload as multipart field "image".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if img_file.size > 10 * 1024 * 1024:   # 10 MB cap
            return Response(
                {'error': 'Image too large. Max 10 MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            text   = _run_ocr(img_file.read())
            fields = _extract_fields(text)
            log.info(
                f'[Scanner] OCR complete: '
                f'doc_num={fields.get("document_number")} '
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
    """
    POST /api/v1/scanner/scan-and-search/
    Same as ScanView, but also queries EDMS for existing documents
    matching the extracted document_number.
    Returns: {fields: {...}, matches: [{document_id, document_number, title, status}]}
    """
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
