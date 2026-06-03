from app.config import get_settings
from app.utils.logging import get_logger
from app.vectorstore.base import SearchResult, VectorPoint, VectorStoreAdapter

logger = get_logger(__name__)

_VECTOR_SIZE = 384


class QdrantAdapter(VectorStoreAdapter):
    def __init__(self):
        from qdrant_client import QdrantClient

        settings = get_settings()
        self._collection = settings.qdrant_collection_name

        self._client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
        )
        self._ensure_collection()
        logger.info("Qdrant adapter initialized", extra={"collection": self._collection})

    def _ensure_collection(self) -> None:
        from qdrant_client.models import Distance, VectorParams

        existing = [c.name for c in self._client.get_collections().collections]
        if self._collection not in existing:
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=_VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info("Created Qdrant collection", extra={"collection": self._collection})

    def upsert(self, points: list[VectorPoint]) -> None:
        from qdrant_client.models import PointStruct

        if not points:
            return

        qdrant_points = [PointStruct(id=p.id, vector=p.vector, payload=p.payload) for p in points]
        self._client.upsert(collection_name=self._collection, points=qdrant_points)
        logger.info("Qdrant upsert", extra={"count": len(points)})

    def search(self, query_vector: list[float], document_id: str, top_k: int) -> list[SearchResult]:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        results = self._client.search(
            collection_name=self._collection,
            query_vector=query_vector,
            query_filter=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
            limit=top_k,
        )

        return [SearchResult(id=str(r.id), score=round(r.score, 4), payload=r.payload or {}) for r in results]

    def delete_document(self, document_id: str) -> int:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        # Count before delete
        count_result = self._client.count(
            collection_name=self._collection,
            count_filter=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
        )
        count = count_result.count

        self._client.delete(
            collection_name=self._collection,
            points_selector=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
        )
        logger.info("Qdrant delete", extra={"document_id": document_id, "deleted": count})
        return count

    def health_check(self) -> bool:
        try:
            self._client.get_collections()
            return True
        except Exception:
            return False
