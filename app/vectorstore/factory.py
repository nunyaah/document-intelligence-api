from app.vectorstore.base import VectorStoreAdapter
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


def create_vector_store() -> VectorStoreAdapter:
    """Instantiate the configured vector store adapter."""
    settings = get_settings()
    store_type = settings.vector_store.lower()

    if store_type == "qdrant":
        if not settings.qdrant_url:
            logger.warning("QDRANT_URL not set, falling back to ChromaDB")
            store_type = "chroma"
        else:
            from app.vectorstore.qdrant_adapter import QdrantAdapter
            return QdrantAdapter()

    from app.vectorstore.chroma_adapter import ChromaAdapter
    return ChromaAdapter()
