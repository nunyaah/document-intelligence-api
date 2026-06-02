from app.pipeline.parsers.base import BaseParser, PageText
from app.utils.exceptions import ParseFailedError


class XlsxParser(BaseParser):
    def parse(self, file_path: str) -> list[PageText]:
        """Convert XLSX sheets to text, one page per sheet."""
        try:
            import pandas as pd

            xl = pd.ExcelFile(file_path)
            pages = []
            for sheet_num, sheet_name in enumerate(xl.sheet_names, start=1):
                df = xl.parse(sheet_name)
                if df.empty:
                    continue
                lines = []
                for _, row in df.iterrows():
                    line = " | ".join(f"{col}: {val}" for col, val in row.items() if str(val).strip())
                    if line:
                        lines.append(line)
                text = "\n".join(lines)
                if text.strip():
                    pages.append(PageText(page_number=sheet_num, text=text))
            if not pages:
                raise ParseFailedError(file_path, "No text found in XLSX.")
            return pages
        except ParseFailedError:
            raise
        except Exception as exc:
            raise ParseFailedError(file_path, str(exc)) from exc
