import re

from app.utils.logging import get_logger

logger = get_logger(__name__)

_SOURCE_PATTERN = re.compile(r"\[SOURCE (\d+)\]")


def build_citations(answer: str, chunks: list) -> list[dict]:
    """Parse [SOURCE N] markers in the answer and map to chunk metadata."""
    source_numbers = {int(m) for m in _SOURCE_PATTERN.findall(answer)}

    citations = []
    for n in sorted(source_numbers):
        idx = n - 1  # 0-based
        if idx < 0 or idx >= len(chunks):
            continue
        chunk = chunks[idx]
        payload = chunk.payload
        excerpt = payload.get("text", "")[:200]
        citations.append(
            {
                "source_label": f"SOURCE {n}",
                "chunk_index": payload.get("chunk_index", idx),
                "page_number": payload.get("page_number", 0),
                "source_filename": payload.get("source_filename", ""),
                "excerpt": excerpt,
                "similarity_score": round(chunk.score, 4),
            }
        )

    return citations
