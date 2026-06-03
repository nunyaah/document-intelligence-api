"""FastAPI dependency injection providers."""

from functools import lru_cache


@lru_cache(maxsize=1)
def get_vector_store():
    """Return the configured vector store adapter (singleton)."""
    from app.vectorstore.factory import create_vector_store

    return create_vector_store()
