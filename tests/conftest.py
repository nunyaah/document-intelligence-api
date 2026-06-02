import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_vector_store
from app.vectorstore.base import VectorStoreAdapter, SearchResult


class MockVectorStore(VectorStoreAdapter):
    def __init__(self):
        self._data: dict[str, list] = {}

    def upsert(self, points):
        for p in points:
            doc_id = p.payload.get("document_id", "test")
            self._data.setdefault(doc_id, []).append(p)

    def search(self, query_vector, document_id, top_k):
        points = self._data.get(document_id, [])[:top_k]
        return [
            SearchResult(id=p.id, score=0.85, payload=p.payload)
            for p in points
        ]

    def delete_document(self, document_id):
        n = len(self._data.pop(document_id, []))
        return n

    def health_check(self):
        return True


@pytest.fixture
def mock_vector_store():
    return MockVectorStore()


@pytest.fixture
def client(mock_vector_store):
    app.dependency_overrides[get_vector_store] = lambda: mock_vector_store
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
