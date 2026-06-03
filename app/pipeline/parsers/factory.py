from app.pipeline.parsers.base import BaseParser
from app.utils.exceptions import InvalidFileTypeError

_ACCEPTED = ["pdf", "docx", "txt", "csv", "xlsx"]


def get_parser(extension: str) -> BaseParser:
    """Return the appropriate parser for the given file extension."""
    ext = extension.lower().lstrip(".")

    if ext == "pdf":
        from app.pipeline.parsers.pdf_parser import PDFParser

        return PDFParser()
    if ext == "docx":
        from app.pipeline.parsers.docx_parser import DocxParser

        return DocxParser()
    if ext == "txt":
        from app.pipeline.parsers.txt_parser import TxtParser

        return TxtParser()
    if ext == "csv":
        from app.pipeline.parsers.csv_parser import CsvParser

        return CsvParser()
    if ext == "xlsx":
        from app.pipeline.parsers.xlsx_parser import XlsxParser

        return XlsxParser()

    raise InvalidFileTypeError(f".{ext}", _ACCEPTED)
