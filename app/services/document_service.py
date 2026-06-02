import uuid
from datetime import datetime, timezone
from fastapi import Depends

from app.dependencies import get_vector_store
from app.pipeline.ingestion import ingest_document
from app.pipeline.embedder import embed_query
from app.pipeline.llm_engine import generate_answer
from app.pipeline.citation_builder import build_citations
from app.vectorstore.base import VectorStoreAdapter
from app.utils.exceptions import DocumentNotFoundError
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

# In-memory document metadata store (session-scoped for MVP)
_document_store: dict[str, dict] = {}


class DocumentService:
    def __init__(self, vector_store: VectorStoreAdapter):
        self._vs = vector_store

    async def ingest_document(self, content: bytes, filename: str, request_id: str = "") -> dict:
        document_id = str(uuid.uuid4())
        ingested_at = datetime.now(timezone.utc).isoformat()

        result = await ingest_document(
            content=content,
            filename=filename,
            document_id=document_id,
            vector_store=self._vs,
            request_id=request_id,
        )

        meta = {
            "document_id": document_id,
            "filename": filename,
            "file_size_bytes": len(content),
            "page_count": result["page_count"],
            "chunk_count": result["chunk_count"],
            "ingested_at": ingested_at,
        }
        _document_store[document_id] = meta
        return meta

    async def query_document(
        self,
        document_id: str,
        question: str,
        top_k: int,
        request_id: str = "",
    ) -> dict:
        if document_id not in _document_store:
            raise DocumentNotFoundError(document_id)

        doc_meta = _document_store[document_id]
        settings = get_settings()

        # Embed query
        query_vector = embed_query(question)

        # Retrieve
        results = self._vs.search(query_vector, document_id=document_id, top_k=top_k)
        logger.info("Retrieval complete", extra={
            "request_id": request_id,
            "document_id": document_id,
            "chunks_retrieved": len(results),
            "top_score": results[0].score if results else 0,
        })

        # Sort by chunk_index for narrative coherence
        results_sorted = sorted(results, key=lambda r: r.payload.get("chunk_index", 0))

        # Generate answer
        answer, model_used = await generate_answer(
            question=question,
            chunks=results_sorted,
            filename=doc_meta["filename"],
        )
        logger.info("LLM call complete", extra={
            "request_id": request_id,
            "model": model_used,
        })

        # Build citations
        citations = build_citations(answer, results_sorted)

        return {
            "answer": answer,
            "citations": citations,
            "model_used": model_used,
            "chunks_retrieved": len(results),
        }

    def list_documents(self) -> list[dict]:
        return list(_document_store.values())

    async def delete_document(self, document_id: str) -> int:
        if document_id not in _document_store:
            raise DocumentNotFoundError(document_id)
        deleted = self._vs.delete_document(document_id)
        del _document_store[document_id]
        return deleted


def get_document_service(vs: VectorStoreAdapter = Depends(get_vector_store)) -> DocumentService:
    return DocumentService(vs)
