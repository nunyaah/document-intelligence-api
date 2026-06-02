import os
import uuid
from pathlib import Path

from app.pipeline.parsers.factory import get_parser
from app.pipeline.chunker import chunk_pages
from app.pipeline.embedder import embed_texts
from app.vectorstore.base import VectorStoreAdapter, VectorPoint
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def ingest_document(
    content: bytes,
    filename: str,
    document_id: str,
    vector_store: VectorStoreAdapter,
    request_id: str = "",
) -> dict:
    """Orchestrate: save file → parse → chunk → embed → store → return metadata."""
    settings = get_settings()

    ext = Path(filename).suffix.lower().lstrip(".")

    # Save temp file
    doc_dir = os.path.join(settings.upload_dir, document_id)
    os.makedirs(doc_dir, exist_ok=True)
    file_path = os.path.join(doc_dir, filename)
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        # Parse
        parser = get_parser(ext)
        pages = parser.parse(file_path)
        page_count = len(pages)
        char_count = sum(len(p.text) for p in pages)
        logger.info("Parsing complete", extra={
            "request_id": request_id,
            "document_id": document_id,
            "page_count": page_count,
            "char_count": char_count,
        })

        # Chunk
        chunks = chunk_pages(pages, document_id=document_id, source_filename=filename)

        # Embed
        texts = [c.text for c in chunks]
        vectors = embed_texts(texts)
        logger.info("Embedding complete", extra={
            "request_id": request_id,
            "document_id": document_id,
            "chunk_count": len(chunks),
        })

        # Build VectorPoints
        points = [
            VectorPoint(
                id=str(uuid.uuid4()),
                vector=vectors[i],
                payload={
                    "document_id": chunks[i].document_id,
                    "chunk_index": chunks[i].chunk_index,
                    "page_number": chunks[i].page_number,
                    "source_filename": chunks[i].source_filename,
                    "char_start": chunks[i].char_start,
                    "char_end": chunks[i].char_end,
                    "created_at": chunks[i].created_at,
                    "text": chunks[i].text,
                },
            )
            for i in range(len(chunks))
        ]

        # Store
        vector_store.upsert(points)
        logger.info("Vector upsert complete", extra={
            "request_id": request_id,
            "document_id": document_id,
            "point_count": len(points),
        })

        return {
            "page_count": page_count,
            "chunk_count": len(chunks),
        }
    finally:
        if not settings.keep_uploaded_files:
            try:
                os.remove(file_path)
                os.rmdir(doc_dir)
            except OSError:
                pass
