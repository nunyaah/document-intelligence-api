from app.pipeline.parsers.base import BaseParser, PageText
from app.utils.exceptions import ParseFailedError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DocxParser(BaseParser):
    def parse(self, file_path: str) -> list[PageText]:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document

            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs)
            if not text.strip():
                raise ParseFailedError(file_path, "No text found in document.")
            return [PageText(page_number=1, text=text)]
        except ParseFailedError:
            raise
        except Exception as exc:
            raise ParseFailedError(file_path, str(exc)) from exc
