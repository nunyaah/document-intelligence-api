from app.pipeline.chunker import chunk_pages
from app.pipeline.parsers.base import PageText


def test_chunker_produces_chunks():
    pages = [PageText(page_number=1, text="Hello world. " * 100)]
    chunks = chunk_pages(pages, document_id="test-doc", source_filename="test.txt")
    assert len(chunks) > 1


def test_chunker_metadata():
    pages = [PageText(page_number=3, text="A " * 300)]
    chunks = chunk_pages(pages, document_id="doc-123", source_filename="report.pdf")
    assert chunks[0].document_id == "doc-123"
    assert chunks[0].source_filename == "report.pdf"
    assert chunks[0].page_number == 3
    assert chunks[0].chunk_index == 0


def test_chunker_consecutive_indices():
    pages = [PageText(page_number=1, text="word " * 500)]
    chunks = chunk_pages(pages, document_id="x", source_filename="f.txt")
    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(chunks)))


def test_chunker_text_not_empty():
    pages = [PageText(page_number=1, text="Some content here. " * 50)]
    chunks = chunk_pages(pages, document_id="d", source_filename="f.txt")
    for c in chunks:
        assert c.text.strip()
