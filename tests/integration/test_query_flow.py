import pytest

from app.services.document_service import _document_store


@pytest.fixture(autouse=True)
def seed_document():
    """Seed a fake document into the in-memory store for query tests."""
    _document_store["test-doc-id"] = {
        "document_id": "test-doc-id",
        "filename": "sample.pdf",
        "file_size_bytes": 1024,
        "page_count": 5,
        "chunk_count": 20,
        "ingested_at": "2026-06-02T00:00:00Z",
    }
    yield
    _document_store.pop("test-doc-id", None)


@pytest.fixture(autouse=True)
def mock_pipeline(monkeypatch):
    """Mock embed and LLM so tests don't need real API keys."""
    monkeypatch.setattr(
        "app.services.document_service.embed_query",
        lambda q: [0.1] * 384,
    )

    async def fake_generate(question, chunks, filename, conversation_history=None):
        return "The answer is based on the document [SOURCE 1].", "llama-3.1-8b-instant"

    monkeypatch.setattr(
        "app.services.document_service.generate_answer",
        fake_generate,
    )


def test_ask_returns_answer(client, mock_vector_store):
    # Seed a chunk into the mock store
    from app.vectorstore.base import VectorPoint

    mock_vector_store.upsert(
        [
            VectorPoint(
                id="point-1",
                vector=[0.1] * 384,
                payload={
                    "document_id": "test-doc-id",
                    "chunk_index": 0,
                    "page_number": 1,
                    "source_filename": "sample.pdf",
                    "char_start": 0,
                    "char_end": 50,
                    "created_at": "2026-06-02T00:00:00Z",
                    "text": "This is the content of the document.",
                },
            )
        ]
    )

    response = client.post(
        "/api/v1/ask",
        json={
            "document_id": "test-doc-id",
            "question": "What is the main topic?",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "answer" in data
    assert data["model_used"] == "llama-3.1-8b-instant"
    assert "citations" in data


def test_ask_missing_document_returns_404(client):
    response = client.post(
        "/api/v1/ask",
        json={
            "document_id": "00000000-0000-4000-a000-000000000000",
            "question": "What is the topic?",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


def test_ask_invalid_document_id_returns_422(client):
    response = client.post(
        "/api/v1/ask",
        json={
            "document_id": "not-a-uuid",
            "question": "What is the topic?",
        },
    )
    assert response.status_code == 422


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "healthy"
    assert "components" in data
