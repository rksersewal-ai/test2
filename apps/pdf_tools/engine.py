# =============================================================================
# FILE: apps/pdf_tools/engine.py
# SPRINT 6 — PDF Merge / Split / Rotate / Extract-pages engine
#
# Uses PyMuPDF (fitz) as primary engine — fast, pure-Python, LAN-safe.
# Falls back to pikepdf for edge cases (encrypted PDFs, XFA forms).
#
# All operations work on file paths inside MEDIA_ROOT.
# Output files are written to MEDIA_ROOT/pdf_ops/<job_id>/
# =============================================================================
import logging
import os
import uuid
from pathlib import Path
from typing  import List, Optional

from django.conf import settings

log     = logging.getLogger('pdf_tools')
OPS_DIR = Path(settings.MEDIA_ROOT) / 'pdf_ops'
OPS_DIR.mkdir(parents=True, exist_ok=True)


def _job_dir() -> Path:
    """Create a unique output directory for one operation."""
    d = OPS_DIR / uuid.uuid4().hex
    d.mkdir(parents=True, exist_ok=True)
    return d


def _abs(relative_path: str) -> Path:
    """Resolve a MEDIA_ROOT-relative path to an absolute Path."""
    return Path(settings.MEDIA_ROOT) / relative_path


# ---------------------------------------------------------------------------
# MERGE
# ---------------------------------------------------------------------------

def merge_pdfs(file_paths: List[str], output_name: str = 'merged.pdf') -> str:
    """
    Merge multiple PDFs into one.
    file_paths: list of MEDIA_ROOT-relative paths.
    Returns MEDIA_ROOT-relative path of the output file.
    """
    import fitz   # PyMuPDF
    out_dir  = _job_dir()
    out_path = out_dir / output_name

    result = fitz.open()
    for rel in file_paths:
        src = fitz.open(str(_abs(rel)))
        result.insert_pdf(src)
        src.close()

    result.save(str(out_path))
    result.close()
    log.info(f'[PDF] Merged {len(file_paths)} files → {out_path}')
    return str(out_path.relative_to(settings.MEDIA_ROOT))


# ---------------------------------------------------------------------------
# SPLIT
# ---------------------------------------------------------------------------

def split_pdf(
    file_path: str,
    page_ranges: Optional[List[List[int]]] = None,
    pages_per_chunk: Optional[int] = None,
) -> List[str]:
    """
    Split a PDF into multiple files.

    Mode A — page_ranges: list of [start, end] pairs (1-indexed, inclusive).
      e.g. [[1, 5], [6, 10], [11, 20]]

    Mode B — pages_per_chunk: split evenly every N pages.
      e.g. pages_per_chunk=10 splits a 35-page PDF into 4 files.

    Returns list of MEDIA_ROOT-relative paths.
    """
    import fitz
    src      = fitz.open(str(_abs(file_path)))
    total    = src.page_count
    out_dir  = _job_dir()
    outputs  = []

    if page_ranges:
        ranges = [(r[0] - 1, r[1] - 1) for r in page_ranges]   # convert to 0-indexed
    elif pages_per_chunk:
        ranges = [
            (i, min(i + pages_per_chunk - 1, total - 1))
            for i in range(0, total, pages_per_chunk)
        ]
    else:
        raise ValueError('Provide either page_ranges or pages_per_chunk.')

    for idx, (start, end) in enumerate(ranges, 1):
        out  = fitz.open()
        out.insert_pdf(src, from_page=start, to_page=end)
        fname = out_dir / f'part_{idx:03d}.pdf'
        out.save(str(fname))
        out.close()
        outputs.append(str(fname.relative_to(settings.MEDIA_ROOT)))

    src.close()
    log.info(f'[PDF] Split {file_path} → {len(outputs)} parts')
    return outputs


# ---------------------------------------------------------------------------
# ROTATE
# ---------------------------------------------------------------------------

def rotate_pdf(
    file_path: str,
    angle: int,                         # 90, 180, 270
    page_numbers: Optional[List[int]] = None,   # 1-indexed; None = all pages
    output_name: str = 'rotated.pdf',
) -> str:
    """
    Rotate specified pages (or all pages) by angle degrees.
    Returns MEDIA_ROOT-relative path.
    """
    import fitz
    if angle not in (90, 180, 270):
        raise ValueError('angle must be 90, 180, or 270')

    src      = fitz.open(str(_abs(file_path)))
    out_dir  = _job_dir()
    out_path = out_dir / output_name
    targets  = {p - 1 for p in page_numbers} if page_numbers else set(range(src.page_count))

    for i, page in enumerate(src):
        if i in targets:
            page.set_rotation((page.rotation + angle) % 360)

    src.save(str(out_path))
    src.close()
    log.info(f'[PDF] Rotated pages {page_numbers or "all"} by {angle}° → {out_path}')
    return str(out_path.relative_to(settings.MEDIA_ROOT))


# ---------------------------------------------------------------------------
# EXTRACT PAGES
# ---------------------------------------------------------------------------

def extract_pages(
    file_path: str,
    page_numbers: List[int],            # 1-indexed
    output_name: str = 'extracted.pdf',
) -> str:
    """
    Extract specific pages from a PDF into a new file.
    Returns MEDIA_ROOT-relative path.
    """
    import fitz
    src      = fitz.open(str(_abs(file_path)))
    out_dir  = _job_dir()
    out_path = out_dir / output_name
    indices  = sorted(set(p - 1 for p in page_numbers if 0 < p <= src.page_count))

    out = fitz.open()
    for i in indices:
        out.insert_pdf(src, from_page=i, to_page=i)

    out.save(str(out_path))
    out.close()
    src.close()
    log.info(f'[PDF] Extracted pages {page_numbers} → {out_path}')
    return str(out_path.relative_to(settings.MEDIA_ROOT))


# ---------------------------------------------------------------------------
# PDF METADATA READER (used by Sanity Checker)
# ---------------------------------------------------------------------------

def get_pdf_info(file_path: str) -> dict:
    """
    Return basic metadata for a PDF: page_count, title, author, is_encrypted.
    """
    try:
        import fitz
        doc  = fitz.open(str(_abs(file_path)))
        meta = doc.metadata or {}
        info = {
            'page_count':   doc.page_count,
            'title':        meta.get('title', ''),
            'author':       meta.get('author', ''),
            'is_encrypted': doc.is_encrypted,
            'file_size_kb': round(_abs(file_path).stat().st_size / 1024, 1),
        }
        doc.close()
        return info
    except Exception as e:
        return {'error': str(e)}
