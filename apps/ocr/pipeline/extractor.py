"""Text extraction layer.

Order of preference:
  1. If PDF has embedded text (pdfminer) → use it directly, confidence = 99.0
  2. Else → convert to images (pdf2image / Pillow) → preprocess → Tesseract

All external libs are optional-import guarded so the module loads even if
not yet installed; RuntimeError raised at call time if library missing.
"""
import os
import logging

logger = logging.getLogger(__name__)


def extract_text_and_confidence(file_path: str) -> tuple[str, float, int]:
    """Return (full_text, confidence_0_to_100, page_count)."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        text, is_native = _try_pdfminer(file_path)
        if is_native and len(text.strip()) > 50:
            return text, 99.0, _count_pdf_pages(file_path)
        # Scanned PDF — fall through to Tesseract
        return _tesseract_pdf(file_path)
    else:
        return _tesseract_image(file_path)


def _try_pdfminer(path: str) -> tuple[str, bool]:
    try:
        from pdfminer.high_level import extract_text as pm_extract
        text = pm_extract(path)
        return text or '', bool(text and text.strip())
    except ImportError:
        logger.warning('pdfminer.six not installed; falling back to Tesseract.')
        return '', False
    except Exception as exc:  # noqa: BLE001
        logger.warning('pdfminer failed for %s: %s', path, exc)
        return '', False


def _count_pdf_pages(path: str) -> int:
    try:
        from pdfminer.pdfpage import PDFPage
        with open(path, 'rb') as f:
            return sum(1 for _ in PDFPage.get_pages(f))
    except Exception:  # noqa: BLE001
        return 1


def _tesseract_pdf(path: str) -> tuple[str, float, int]:
    try:
        from pdf2image import convert_from_path
    except ImportError as exc:
        raise RuntimeError('pdf2image is required for scanned PDFs.') from exc
    pages = convert_from_path(path, dpi=300)
    texts, confidences = [], []
    for img in pages:
        t, c = _run_tesseract(img)
        texts.append(t)
        confidences.append(c)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    return '\n\n'.join(texts), avg_conf, len(pages)


def _tesseract_image(path: str) -> tuple[str, float, int]:
    from PIL import Image
    img = Image.open(path)
    t, c = _run_tesseract(img)
    return t, c, 1


def _run_tesseract(img) -> tuple[str, float]:
    try:
        import pytesseract
        from PIL import ImageFilter, ImageEnhance
        import numpy as np
    except ImportError as exc:
        raise RuntimeError('pytesseract / Pillow / numpy required.') from exc

    # Basic preprocessing: grayscale, sharpen, contrast boost
    img = img.convert('L')
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(2.0)

    data = pytesseract.image_to_data(img, lang='eng', output_type=pytesseract.Output.DICT)
    words = [w for w, c in zip(data['text'], data['conf']) if w.strip() and int(c) > 0]
    confs = [int(c) for c in data['conf'] if int(c) > 0]
    full_text = pytesseract.image_to_string(img, lang='eng')
    avg_conf = sum(confs) / len(confs) if confs else 0.0
    return full_text, avg_conf
