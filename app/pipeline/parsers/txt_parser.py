from app.pipeline.parsers.base import BaseParser, PageText
from app.utils.exceptions import ParseFailedError


class TxtParser(BaseParser):
    def parse(self, file_path: str) -> list[PageText]:
        """Read plain text file with encoding detection."""
        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    text = f.read().strip()
                if not text:
                    raise ParseFailedError(file_path, "File is empty.")
                return [PageText(page_number=1, text=text)]
            except (UnicodeDecodeError, LookupError):
                continue
            except ParseFailedError:
                raise
        raise ParseFailedError(file_path, "Could not decode file with any supported encoding.")
