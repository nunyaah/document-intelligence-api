import io
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


def _make_pdf_bytes():
    """Create minimal valid PDF bytes."""
    try:
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Integration test document. " * 50)
        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()
    except ImportError:
        # Minimal fake PDF
        return b"%PDF-1.4\n% test\n"


@pytest.fixture(autouse=True)
def mock_ingest(monkeypatch):
    """Prevent real embedding/vector operations during upload tests."""
    async def fake_ingest(content, filename, document_id, vector_store, request_id=""):
        return {"page_count": 5, "chunk_count": 20}

    monkeypatch.setattr("app.services.document_service.ingest_document", fake_ingest)


def test_upload_pdf_success(client):
    pdf_bytes = _make_pdf_bytes()
    response = client.post(
        "/api/v1/upload",
        files={"file": ("report.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "document_id" in data["data"]
    assert data["data"]["filename"] == "report.pdf"
    assert data["data"]["chunk_count"] == 20


def test_upload_invalid_extension_returns_415(client):
    response = client.post(
        "/api/v1/upload",
        files={"file": ("malware.exe", b"MZ\x90\x00", "application/octet-stream")},
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "INVALID_FILE_TYPE"


def test_upload_empty_file_returns_400(client):
    response = client.post(
        "/api/v1/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMPTY_FILE"


def test_upload_too_large_returns_413(client):
    big = b"%PDF" + b"x" * (21 * 1024 * 1024)
    response = client.post(
        "/api/v1/upload",
        files={"file": ("big.pdf", big, "application/pdf")},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_get_documents_lists_uploaded(client):
    # Upload first
    pdf_bytes = _make_pdf_bytes()
    client.post("/api/v1/upload", files={"file": ("test.pdf", pdf_bytes, "application/pdf")})

    r = client.get("/api/v1/documents")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] >= 1
