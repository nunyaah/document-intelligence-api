# Document Intelligence API

> **Upload any document. Ask it anything. Get cited answers.**

A production-grade Retrieval-Augmented Generation (RAG) system built with FastAPI, LangChain, Groq, and Qdrant — deployable at **$0** using free tiers.

---

## Features

- **Multi-format ingestion** — PDF, DOCX, TXT, CSV, XLSX
- **Semantic search** — SentenceTransformers embeddings (local, no API key)
- **Dual vector store** — Qdrant Cloud (primary) or ChromaDB (local fallback)
- **Cited answers** — LLM responses with `[SOURCE N]` references mapped to page numbers
- **RAGAS evaluation** — automated quality metrics (Faithfulness, Relevancy, Precision, Recall)
- **Clean web UI** — drag-and-drop upload, chat interface, collapsible citations panel
- **Production patterns** — structured JSON logging, request ID propagation, rate limiting, retry logic
- **Docker-ready** — single `docker-compose up` to run everything

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.11+) |
| RAG Framework | LangChain Text Splitters |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (free, local) |
| Vector DB (primary) | Qdrant Cloud free tier |
| Vector DB (fallback) | ChromaDB (local, no API key) |
| LLM | Groq API — Llama 3.1 8B (free tier) |
| Evaluation | RAGAS |
| Frontend | Vanilla HTML + Tailwind CSS + JS |
| Containerization | Docker + docker-compose |
| Deployment | Render / Hugging Face Spaces |

---

## Quick Start

```bash
git clone https://github.com/{username}/document-intelligence-api
cd document-intelligence-api

cp .env.example .env
# Fill in GROQ_API_KEY (free at console.groq.com)
# VECTOR_STORE=chroma works without any additional API key

# Option 1: Docker (recommended)
docker-compose up --build
# Visit http://localhost:8000

# Option 2: Manual
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | **Required.** Free at [console.groq.com](https://console.groq.com) |
| `VECTOR_STORE` | `chroma` | `qdrant` or `chroma` |
| `QDRANT_URL` | — | Qdrant Cloud cluster URL (if using Qdrant) |
| `QDRANT_API_KEY` | — | Qdrant Cloud API key (if using Qdrant) |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Groq model name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformers model |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `RETRIEVAL_TOP_K` | `5` | Chunks retrieved per query |
| `RETRIEVAL_MIN_SCORE` | `0.3` | Minimum cosine similarity threshold |
| `MAX_FILE_SIZE_MB` | `20` | Maximum upload file size |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `RATE_LIMIT_PER_MINUTE` | `10` | Requests per minute per IP |

See [.env.example](.env.example) for the full list.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/upload` | Upload and ingest a document |
| `POST` | `/api/v1/ask` | Ask a question about a document |
| `GET` | `/api/v1/documents` | List all ingested documents |
| `DELETE` | `/api/v1/documents/{id}` | Delete a document and its vectors |
| `GET` | `/api/v1/health` | Health check (vector store, LLM, embedder) |
| `POST` | `/api/v1/eval` | Run RAGAS evaluation |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## RAGAS Evaluation Scores

Evaluated against 5 Q&A pairs on a sample document:

| Metric | Score | Target |
|---|---|---|
| Faithfulness | — | ≥ 0.80 |
| Answer Relevancy | — | ≥ 0.75 |
| Context Precision | — | ≥ 0.75 |
| Context Recall | — | ≥ 0.70 |

_Run evaluation yourself:_
```bash
python scripts/run_eval.py \
  --document_id <uuid> \
  --eval_file tests/eval_dataset.json \
  --output eval_results.json
```

---

## Project Structure

```
document-intelligence-api/
├── app/
│   ├── main.py                    # FastAPI app, middleware, lifespan
│   ├── config.py                  # Settings (pydantic-settings)
│   ├── dependencies.py            # FastAPI DI providers
│   ├── api/v1/                    # Route handlers
│   ├── pipeline/                  # Parsers, chunker, embedder, LLM, citations
│   ├── vectorstore/               # Qdrant + ChromaDB adapters
│   ├── services/                  # Document & eval business logic
│   └── utils/                     # Exceptions, logging, file validation
├── frontend/                      # Static HTML/CSS/JS UI
├── tests/                         # Unit + integration tests
├── scripts/                       # CLI tools (eval, seed, model download)
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Architecture

```
Client (Browser / API)
        │ HTTP/REST
        ▼
  FastAPI Backend
  ┌─────────────────────────────────┐
  │ /upload  /ask  /documents  /eval│
  │           │                     │
  │  Parser → Chunker → Embedder    │
  │                  │              │
  │         Vector Store Adapter    │
  │         (Qdrant | ChromaDB)     │
  │                                 │
  │  Retrieval → LLM Engine → Citations
  └─────────────────────────────────┘
        │              │
   Qdrant Cloud    Groq API
```

---

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Lint
ruff check .

# Format
black .
```

---

## Deployment

### Render (Free Tier)
1. Connect GitHub repo to [Render](https://render.com)
2. Set env vars in the Render dashboard
3. Build: `pip install -r requirements.txt && python scripts/download_model.py`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Hugging Face Spaces (Docker SDK)
1. Create a new Space with Docker SDK
2. Push this repo — the `Dockerfile` handles everything

---

## License

[MIT](LICENSE)
