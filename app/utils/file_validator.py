import os
from pathlib import Path

from app.utils.exceptions import InvalidFileTypeError, FileTooLargeError, EmptyFileError

ACCEPTED_EXTENSIONS = ["pdf", "docx", "txt", "csv", "xlsx"]
ACCEPTED_MIMES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

# Magic byte signatures
_PDF_MAGIC = b"%PDF"
_ZIP_MAGIC = b"PK"  # DOCX and XLSX are ZIP-based


def _detect_by_magic(header: bytes) -> str | None:
    if header[:4] == _PDF_MAGIC:
        return "pdf"
    if header[:2] == _ZIP_MAGIC:
        return "zip"  # could be docx or xlsx
    return None


def validate_file(filename: str, content: bytes, max_bytes: int) -> str:
    """Validate file type and size. Returns the detected extension."""
    if not content:
        raise EmptyFileError()

    size = len(content)
    if size > max_bytes:
        raise FileTooLargeError(size / (1024 * 1024), max_bytes // (1024 * 1024))

    ext = Path(filename).suffix.lower().lstrip(".")
    magic_type = _detect_by_magic(content[:8])

    # Cross-check magic with extension
    if magic_type == "pdf" and ext != "pdf":
        raise InvalidFileTypeError(f".{ext}", ACCEPTED_EXTENSIONS)
    if magic_type == "zip" and ext not in ("docx", "xlsx"):
        raise InvalidFileTypeError(f".{ext}", ACCEPTED_EXTENSIONS)

    if ext not in ACCEPTED_EXTENSIONS:
        raise InvalidFileTypeError(f".{ext}" if ext else "(no extension)", ACCEPTED_EXTENSIONS)

    return ext


def sanitize_filename(filename: str) -> str:
    """Remove path traversal and sanitize filename for safe storage."""
    name = os.path.basename(filename)
    name = name.replace(" ", "_")
    # Keep only safe chars
    safe = "".join(c for c in name if c.isalnum() or c in "._-")
    return safe or "upload"
