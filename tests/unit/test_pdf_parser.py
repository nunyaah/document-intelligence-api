import pytest

from app.pipeline.parsers.pdf_parser import PDFParser
from app.utils.exceptions import EncryptedFileError


def test_parse_pdf_returns_page_texts(tmp_path):
    """PDF parser returns PageText objects with page numbers."""
    pdf_path = str(tmp_path / "test.pdf")
    # Create a minimal PDF using fitz
    try:
        import fitz

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Hello from page one.")
        doc.save(pdf_path)
        doc.close()
    except ImportError:
        pytest.skip("fitz not installed")

    parser = PDFParser()
    pages = parser.parse(pdf_path)
    assert len(pages) >= 1
    assert pages[0].page_number == 1
    assert "Hello" in pages[0].text


def test_pdf_parser_encrypted_raises(tmp_path):
    """Encrypted PDF raises EncryptedFileError."""
    pdf_path = str(tmp_path / "enc.pdf")
    try:
        import fitz

        doc = fitz.open()
        doc.new_page()
        doc.save(pdf_path, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="secret")
        doc.close()
    except ImportError:
        pytest.skip("fitz not installed")

    parser = PDFParser()
    with pytest.raises(EncryptedFileError):
        parser.parse(pdf_path)
