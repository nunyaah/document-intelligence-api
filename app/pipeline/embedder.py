from functools import lru_cache

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_embedder():
    """Lazy singleton for the SentenceTransformer embedding model."""
    from sentence_transformers import SentenceTransformer

    settings = get_settings()
    model_name = settings.embedding_model
    logger.info("Loading embedding model", extra={"model": model_name})
    model = SentenceTransformer(model_name, cache_folder=settings.embedding_cache_dir)
    logger.info("Embedding model loaded", extra={"model": model_name})
    return model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts and return 384-dim vectors."""
    model = get_embedder()
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([text])[0]
