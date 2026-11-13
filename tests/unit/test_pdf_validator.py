import pytest

from policy_assistant.infrastructure.pdf.pdf_validator import (
    PDFValidator,
    MAX_FILE_SIZE,
)


def test_valid_pdf_is_accepted(tmp_path):
    pdf_file = tmp_path / "valid.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\nSample PDF content")

    PDFValidator().validate(str(pdf_file))


def test_missing_file_is_rejected(tmp_path):
    pdf_file = tmp_path / "missing.pdf"

    with pytest.raises(ValueError, match="does not exist"):
        PDFValidator().validate(str(pdf_file))


def test_wrong_extension_is_rejected(tmp_path):
    file = tmp_path / "document.txt"
    file.write_bytes(b"%PDF-1.4\nContent")

    with pytest.raises(ValueError, match="Only PDF files"):
        PDFValidator().validate(str(file))


def test_invalid_pdf_signature_is_rejected(tmp_path):
    pdf_file = tmp_path / "invalid.pdf"
    pdf_file.write_bytes(b"This is not a PDF")

    with pytest.raises(ValueError, match="signature"):
        PDFValidator().validate(str(pdf_file))


def test_oversized_pdf_is_rejected(tmp_path):
    pdf_file = tmp_path / "large.pdf"
    pdf_file.write_bytes(b"%PDF-" + b"A" * MAX_FILE_SIZE)

    with pytest.raises(ValueError, match="10 MB limit"):
        PDFValidator().validate(str(pdf_file))