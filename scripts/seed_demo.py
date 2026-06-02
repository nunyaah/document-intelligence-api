#!/usr/bin/env python3
"""Upload a sample document and ask demo questions."""
import sys
import httpx

BASE = "http://localhost:8000"
SAMPLE = "tests/fixtures/sample.pdf"
QUESTIONS = [
    "What is the main topic of this document?",
    "Summarize the key points.",
    "What conclusions does the document draw?",
]


def main():
    with open(SAMPLE, "rb") as f:
        files = {"file": (SAMPLE.split("/")[-1], f, "application/pdf")}
        r = httpx.post(f"{BASE}/api/v1/upload", files=files, timeout=120)

    r.raise_for_status()
    doc_id = r.json()["data"]["document_id"]
    print(f"Uploaded — document_id: {doc_id}")

    for q in QUESTIONS:
        print(f"\nQ: {q}")
        r = httpx.post(f"{BASE}/api/v1/ask", json={"document_id": doc_id, "question": q}, timeout=60)
        r.raise_for_status()
        data = r.json()["data"]
        print(f"A: {data['answer'][:300]}...")
        if data["citations"]:
            c = data["citations"][0]
            print(f"   [Source: {c['source_filename']} p.{c['page_number']}, score {c['similarity_score']}]")


if __name__ == "__main__":
    main()
