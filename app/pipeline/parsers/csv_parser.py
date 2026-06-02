from app.pipeline.parsers.base import BaseParser, PageText
from app.utils.exceptions import ParseFailedError


class CsvParser(BaseParser):
    def parse(self, file_path: str) -> list[PageText]:
        """Convert CSV rows to text chunks, one page per 100 rows."""
        try:
            import pandas as pd

            df = pd.read_csv(file_path)
            if df.empty:
                raise ParseFailedError(file_path, "CSV file is empty.")

            pages = []
            chunk_size = 100
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i : i + chunk_size]
                # Convert each row to "col: val, col: val" representation
                lines = []
                for _, row in chunk.iterrows():
                    line = " | ".join(f"{col}: {val}" for col, val in row.items() if str(val).strip())
                    if line:
                        lines.append(line)
                text = "\n".join(lines)
                if text.strip():
                    pages.append(PageText(page_number=i // chunk_size + 1, text=text))
            return pages
        except ParseFailedError:
            raise
        except Exception as exc:
            raise ParseFailedError(file_path, str(exc)) from exc
