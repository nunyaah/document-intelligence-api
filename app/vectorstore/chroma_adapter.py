import uuid
from app.vectorstore.base import VectorStoreAdapter, VectorPoint, SearchResult
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ChromaAdapter(VectorStoreAdapter):
    def __init__(self):
        import chromadb

        settings = get_settings()
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self._collection_name = "document_chunks"
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("ChromaDB adapter initialized", extra={"persist_dir": settings.chroma_persist_dir})

    def upsert(self, points: list[VectorPoint]) -> None:
        if not points:
            return
        self._collection.upsert(
            ids=[p.id for p in points],
            embeddings=[p.vector for p in points],
            metadatas=[p.payload for p in points],
        )
        logger.info("ChromaDB upsert", extra={"count": len(points)})

    def search(self, query_vector: list[float], document_id: str, top_k: int) -> list[SearchResult]:
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where={"document_id": document_id},
            include=["metadatas", "distances"],
        )

        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        # ChromaDB cosine distance: score = 1 - distance (range ~0–1 for normalized vectors)
        # No hard threshold here — always return whatever was found so the LLM has context.
        # The LLM's system prompt handles the "not in document" case.
        return [
            SearchResult(id=rid, score=round(1.0 - dist, 4), payload=meta)
            for rid, dist, meta in zip(ids, distances, metadatas)
        ]

    def delete_document(self, document_id: str) -> int:
        existing = self._collection.get(where={"document_id": document_id})
        ids = existing.get("ids", [])
        if ids:
            self._collection.delete(ids=ids)
        logger.info("ChromaDB delete", extra={"document_id": document_id, "deleted": len(ids)})
        return len(ids)

    def health_check(self) -> bool:
        try:
            self._client.heartbeat()
            return True
        except Exception:
            return False
