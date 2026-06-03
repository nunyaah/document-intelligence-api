from app.pipeline.citation_builder import build_citations
from app.vectorstore.base import SearchResult


def _make_chunk(idx, page, text, score=0.9):
    return SearchResult(
        id=f"id-{idx}",
        score=score,
        payload={
            "chunk_index": idx,
            "page_number": page,
            "source_filename": "test.pdf",
            "text": text,
        },
    )


def test_build_citations_extracts_referenced():
    chunks = [
        _make_chunk(0, 1, "The revenue was $4.2B in Q3."),
        _make_chunk(1, 2, "Cloud growth was 41%."),
        _make_chunk(2, 3, "Operating costs rose 12%."),
    ]
    answer = "Revenue was $4.2B [SOURCE 1]. Cloud grew 41% [SOURCE 2]."
    citations = build_citations(answer, chunks)

    assert len(citations) == 2
    assert citations[0]["source_label"] == "SOURCE 1"
    assert citations[0]["page_number"] == 1
    assert citations[1]["source_label"] == "SOURCE 2"
    assert citations[1]["page_number"] == 2


def test_build_citations_ignores_missing():
    chunks = [_make_chunk(0, 1, "Some text.")]
    answer = "The answer references [SOURCE 1] and [SOURCE 5]."
    citations = build_citations(answer, chunks)
    # SOURCE 5 doesn't exist — only SOURCE 1 returned
    assert len(citations) == 1
    assert citations[0]["source_label"] == "SOURCE 1"


def test_build_citations_no_sources():
    chunks = [_make_chunk(0, 1, "Some text.")]
    answer = "I cannot find this information in the provided document."
    citations = build_citations(answer, chunks)
    assert citations == []
