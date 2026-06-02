import re
from app.pipeline.parsers.base import BaseParser, PageText
from app.utils.exceptions import EncryptedFileError, ParseFailedError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PDFParser(BaseParser):
    def parse(self, file_path: str) -> list[PageText]:
        """Extract text from PDF using PyMuPDF with pypdf fallback."""
        try:
            return self._parse_pymupdf(file_path)
        except EncryptedFileError:
            raise
        except Exception as exc:
            logger.warning("PyMuPDF failed, trying pypdf fallback", extra={"error": str(exc)})
            try:
                return self._parse_pypdf(file_path)
            except Exception as exc2:
                raise ParseFailedError(file_path, str(exc2)) from exc2

    def _parse_pymupdf(self, file_path: str) -> list[PageText]:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        if doc.is_encrypted:
            doc.close()
            raise EncryptedFileError()

        pages = []
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text")
            text = self._clean_text(text)
            if text:
                pages.append(PageText(page_number=i, text=text))
        doc.close()

        if not pages:
            raise ParseFailedError(file_path, "No text could be extracted.")
        return pages

    def _parse_pypdf(self, file_path: str) -> list[PageText]:
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        if reader.is_encrypted:
            raise EncryptedFileError()

        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = self._clean_text(text)
            if text:
                pages.append(PageText(page_number=i, text=text))

        if not pages:
            raise ParseFailedError(file_path, "No text could be extracted.")
        return pages

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text.strip()
