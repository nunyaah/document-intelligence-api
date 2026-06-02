from dataclasses import dataclass
from datetime import datetime, timezone

from app.pipeline.parsers.base import PageText
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Chunk:
    document_id: str
    chunk_index: int
    page_number: int
    source_filename: str
    text: str
    char_start: int
    char_end: int
    created_at: str


def chunk_pages(pages: list[PageText], document_id: str, source_filename: str) -> list[Chunk]:
    """Split page texts into overlapping chunks with metadata."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    settings = get_settings()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    texts = [p.text for p in pages]
    metadatas = [{"page_number": p.page_number, "source": source_filename} for p in pages]

    docs = splitter.create_documents(texts=texts, metadatas=metadatas)

    now = datetime.now(timezone.utc).isoformat()
    chunks: list[Chunk] = []

    for i, doc in enumerate(docs):
        text = doc.page_content
        chunks.append(
            Chunk(
                document_id=document_id,
                chunk_index=i,
                page_number=doc.metadata.get("page_number", 0),
                source_filename=source_filename,
                text=text,
                char_start=doc.metadata.get("start_index", 0),
                char_end=doc.metadata.get("start_index", 0) + len(text),
                created_at=now,
            )
        )

    logger.info("Chunking complete", extra={"document_id": document_id, "chunk_count": len(chunks)})
    return chunks
