import uuid
from datetime import datetime, timezone

from fastapi import Depends

from app.dependencies import get_vector_store
from app.pipeline.citation_builder import build_citations
from app.pipeline.embedder import embed_query
from app.pipeline.ingestion import ingest_document
from app.pipeline.llm_engine import generate_answer
from app.utils.exceptions import DocumentNotFoundError
from app.utils.logging import get_logger
from app.vectorstore.base import VectorStoreAdapter

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
        conversation_history: list | None = None,
        request_id: str = "",
    ) -> dict:
        if document_id not in _document_store:
            raise DocumentNotFoundError(document_id)

        doc_meta = _document_store[document_id]

        # Build a contextualized query for embedding so that pronouns like
        # "this strategy" or "it" resolve correctly against prior turns.
        embedding_query = _contextualize_query(question, conversation_history or [])

        # Embed query
        query_vector = embed_query(embedding_query)

        # Retrieve
        results = self._vs.search(query_vector, document_id=document_id, top_k=top_k)
        logger.info(
            "Retrieval complete",
            extra={
                "request_id": request_id,
                "document_id": document_id,
                "chunks_retrieved": len(results),
                "top_score": results[0].score if results else 0,
            },
        )

        # Sort by chunk_index for narrative coherence
        results_sorted = sorted(results, key=lambda r: r.payload.get("chunk_index", 0))

        # Generate answer
        answer, model_used = await generate_answer(
            question=question,
            chunks=results_sorted,
            filename=doc_meta["filename"],
            conversation_history=conversation_history or [],
        )
        logger.info(
            "LLM call complete",
            extra={
                "request_id": request_id,
                "model": model_used,
            },
        )

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


def _contextualize_query(question: str, history: list) -> str:
    """Prepend the last assistant answer to the current question so that
    deictic references like 'this strategy' or 'it' resolve correctly
    during vector similarity search."""
    if not history:
        return question

    # Find the most recent assistant turn and append it as context prefix
    for turn in reversed(history):
        if turn.get("role") == "assistant":
            prior = turn["content"][:400].strip()  # cap to keep embedding focused
            return f"{prior} {question}"

    return question


def get_document_service(vs: VectorStoreAdapter = Depends(get_vector_store)) -> DocumentService:
    return DocumentService(vs)
