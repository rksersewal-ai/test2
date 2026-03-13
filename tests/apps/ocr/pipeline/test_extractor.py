import pytest
from unittest.mock import patch
import sys
from apps.ocr.pipeline.extractor import extract_text_and_confidence, _tesseract_pdf


def test_tesseract_pdf_missing_pdf2image():
    # Simulate missing pdf2image module
    with patch.dict(sys.modules, {'pdf2image': None}):
        with pytest.raises(RuntimeError) as exc_info:
            _tesseract_pdf("dummy.pdf")

        assert "pdf2image is required for scanned PDFs" in str(exc_info.value)


@patch('apps.ocr.pipeline.extractor._tesseract_pdf')
@patch('apps.ocr.pipeline.extractor._try_pdfminer')
def test_extract_text_and_confidence_missing_pdf2image(mock_try_pdfminer, mock_tesseract_pdf):
    # Simulate pdfminer returning non-native
    mock_try_pdfminer.return_value = ('', False)

    # Simulate missing pdf2image in _tesseract_pdf
    mock_tesseract_pdf.side_effect = RuntimeError('pdf2image is required for scanned PDFs.')

    with pytest.raises(RuntimeError) as exc_info:
        extract_text_and_confidence("dummy.pdf")

    assert "pdf2image is required for scanned PDFs" in str(exc_info.value)


def test_extract_text_and_confidence_direct_missing_pdf2image():
    # Complete flow: from extract_text_and_confidence down to _tesseract_pdf
    with patch.dict(sys.modules, {'pdf2image': None}):
        with pytest.raises(RuntimeError) as exc_info:
            extract_text_and_confidence("dummy.pdf")

        assert "pdf2image is required for scanned PDFs" in str(exc_info.value)
