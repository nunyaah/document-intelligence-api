# Product Requirements Document
# Production RAG System — Document Intelligence API

**Version:** 1.0.0
**Date:** 2026-06-02
**Status:** Implementation-Ready
**Repo:** `document-intelligence-api`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Target Users](#3-target-users)
4. [Goals and Non-Goals](#4-goals-and-non-goals)
5. [Success Metrics](#5-success-metrics)
6. [User Personas](#6-user-personas)
7. [User Stories](#7-user-stories)
8. [Functional Requirements](#8-functional-requirements)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [MVP Scope](#10-mvp-scope)
11. [Future Scope](#11-future-scope)
12. [System Architecture](#12-system-architecture)
13. [Data Flow](#13-data-flow)
14. [API Requirements](#14-api-requirements)
15. [UI Requirements](#15-ui-requirements)
16. [File Upload Requirements](#16-file-upload-requirements)
17. [Document Parsing and Chunking Requirements](#17-document-parsing-and-chunking-requirements)
18. [Embedding and Vector Database Requirements](#18-embedding-and-vector-database-requirements)
19. [Retrieval Requirements](#19-retrieval-requirements)
20. [LLM Answer Generation Requirements](#20-llm-answer-generation-requirements)
21. [Citation and Source Reference Requirements](#21-citation-and-source-reference-requirements)
22. [Evaluation Requirements — RAGAS](#22-evaluation-requirements--ragas)
23. [Security and Privacy Requirements](#23-security-and-privacy-requirements)
24. [Error Handling Requirements](#24-error-handling-requirements)
25. [Deployment Requirements](#25-deployment-requirements)
26. [Observability and Logging Requirements](#26-observability-and-logging-requirements)
27. [README / GitHub Portfolio Requirements](#27-readme--github-portfolio-requirements)
28. [Acceptance Criteria](#28-acceptance-criteria)
29. [Technical Risks and Mitigations](#29-technical-risks-and-mitigations)
30. [Suggested Milestones](#30-suggested-milestones)
31. [Recommended Folder Structure](#31-recommended-folder-structure)
32. [Example API Endpoints](#32-example-api-endpoints)
33. [Example Environment Variables](#33-example-environment-variables)
34. [Definition of Done](#34-definition-of-done)
35. [MVP Step-by-Step Checklist](#35-mvp-step-by-step-checklist)

---

## 1. Executive Summary

The **Document Intelligence API** is a portfolio-grade Retrieval-Augmented Generation (RAG) system that enables users to upload documents (PDF, DOCX, XLSX, CSV, images) and ask natural language questions against their content. The system extracts text, chunks it, generates semantic embeddings, stores them in a vector database, retrieves relevant context, and uses a large language model (LLM) to produce grounded answers with source citations.

The project is designed to be:

- **Deployable at $0** using free-tier services and open-source libraries.
- **Demo-grade production-quality** — well-structured, well-documented, and visually polished enough to impress clients, hiring managers, and GitHub visitors.
- **Technically deep** — covering real production patterns: async processing, structured metadata, RAGAS evaluation, observability, Docker containerization, and CI/CD-ready layout.

**Chosen Stack Summary:**

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.11+) |
| Frontend UI | Vanilla HTML/CSS/JS or React (served by FastAPI or separate) |
| RAG Framework | LangChain |
| PDF Parsing | PyMuPDF (`fitz`) + pypdf fallback |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (free, local) |
| Vector DB (primary) | Qdrant free cloud tier or Pinecone free tier |
| Vector DB (fallback) | ChromaDB (local, no API key needed) |
| LLM | Groq API (Llama 3 / Mixtral, free tier) |
| Evaluation | RAGAS |
| Containerization | Docker + docker-compose |
| Deployment | Render free tier / Hugging Face Spaces / Railway |
| Testing | pytest + httpx |

---

## 2. Problem Statement

AI engineers and freelance developers who want to demonstrate RAG expertise face a difficult tradeoff: production-grade RAG systems are expensive to run (OpenAI embeddings, managed vector DBs, hosted LLMs) and complex to build, while toy tutorials are too shallow to impress evaluators.

There is no widely available, complete, open-source RAG reference implementation that:
- Works end-to-end with $0 in API costs.
- Is structured like a real production service (not a Jupyter notebook).
- Includes evaluation metrics, proper error handling, a real UI, Docker, and deployment instructions.
- Is comprehensive enough to showcase to a client or pass a technical screen.

This project fills that gap.

---

## 3. Target Users

### Primary Users (Demo/Portfolio Context)
1. **The developer themselves** — building it as a portfolio piece to showcase AI/LLM engineering skills.
2. **Potential clients** — small business owners, consultants, or researchers seeing the live demo.
3. **Technical hiring managers** — reviewing the GitHub repo or a live deployment link.

### Secondary Users (If Deployed Publicly)
4. **Researchers and analysts** — wanting to query a long PDF without reading it manually.
5. **Students** — wanting to ask questions about textbooks, papers, or notes.

---

## 4. Goals and Non-Goals

### Goals
- Build a complete, working RAG pipeline from upload to cited answer.
- Achieve $0 operational cost using free tiers.
- Present a production-style codebase structure suitable for GitHub showcase.
- Include automated RAGAS evaluation that produces documented metric scores.
- Deploy publicly with a shareable URL.
- Generate comprehensive documentation (README, API docs, architecture diagram).

### Non-Goals
- Handling concurrent heavy production traffic (> 10 simultaneous users).
- Multi-user authentication with isolated document stores per user.
- Real-time streaming responses (nice-to-have, not MVP).
- Fine-tuning the LLM on domain-specific data.
- Mobile-native app (responsive web UI is sufficient).
- Paying for any SaaS product for the MVP.

---

## 5. Success Metrics

| Metric | Target |
|---|---|
| End-to-end upload → answer latency | < 10s for a 10-page PDF (after ingestion) |
| Answer generation latency (query only) | < 5s |
| RAGAS Faithfulness | ≥ 0.80 |
| RAGAS Answer Relevancy | ≥ 0.75 |
| RAGAS Context Precision | ≥ 0.75 |
| RAGAS Context Recall | ≥ 0.70 |
| GitHub stars / forks | Tracked but not a hard gate |
| Supported file types | ≥ 4 (PDF, DOCX, TXT, CSV) |
| Test coverage | ≥ 70% on core pipeline modules |
| Uptime on free hosting | ≥ 95% during demo periods |

---

## 6. User Personas

### Persona 1 — Alex, the AI Engineer Job Seeker
- **Age:** 26, software engineer with 2 years of Python experience.
- **Goal:** Land an AI engineering role at a startup. Needs a strong GitHub portfolio.
- **Pain Point:** Has read RAG tutorials but never shipped a complete, deployable project.
- **Usage:** Will build this project, customize it, and link it from their resume.

### Persona 2 — Sarah, the Freelance AI Consultant
- **Age:** 34, ML practitioner offering LLM consulting services.
- **Goal:** Show clients a live working demo of document intelligence during sales calls.
- **Pain Point:** Existing demos are either too expensive to keep live or too janky to show.
- **Usage:** Deploys the app, uploads a sample client document, and demonstrates it live.

### Persona 3 — Carlos, the Research Analyst
- **Age:** 41, financial analyst who reads 50+ page reports weekly.
- **Goal:** Ask natural language questions against dense PDF reports.
- **Pain Point:** Spending hours ctrl+F-ing through documents.
- **Usage:** Uploads a 50-page annual report, asks 10 questions, reviews citations.

---

## 7. User Stories

### Upload Flow
- **US-01:** As a user, I want to drag-and-drop or click to upload a PDF so I can start asking questions quickly.
- **US-02:** As a user, I want to see a progress indicator during upload and processing so I know the system is working.
- **US-03:** As a user, I want to receive a clear error message if my file is invalid (wrong type, too large) so I know what to fix.
- **US-04:** As a user, I want to upload a DOCX, TXT, or CSV file in addition to PDFs.

### Query Flow
- **US-05:** As a user, I want to type a natural language question and receive an accurate, grounded answer within 5 seconds.
- **US-06:** As a user, I want to see the specific document chunks that were used to generate the answer so I can verify accuracy.
- **US-07:** As a user, I want to see the page number or section reference for each cited chunk.
- **US-08:** As a user, I want to ask follow-up questions about the same document without re-uploading.

### Document Management
- **US-09:** As a user, I want to see a list of documents I have uploaded in the current session.
- **US-10:** As a user, I want to delete a document and its associated vectors.
- **US-11:** As a user, I want to switch between multiple uploaded documents.

### System / API
- **US-12:** As a developer, I want a `/health` endpoint to verify the system is running.
- **US-13:** As a developer, I want interactive API docs at `/docs` so I can test endpoints directly.
- **US-14:** As a developer, I want to run RAGAS evaluation against a test dataset and view scores.

---

## 8. Functional Requirements

### FR-01: File Upload
- Accept multipart form-data file upload.
- Validate file type (allowlist: `.pdf`, `.docx`, `.txt`, `.csv`, `.xlsx`).
- Validate file size (max 20MB for MVP).
- Assign a unique `document_id` (UUID4) to each uploaded document.
- Return upload status and `document_id` in response.

### FR-02: Document Parsing
- Extract raw text from PDF using PyMuPDF (`fitz`).
- Extract raw text from DOCX using `python-docx`.
- Extract raw text from TXT directly.
- Extract rows from CSV using `pandas`.
- Extract rows from XLSX using `openpyxl` or `pandas`.
- Preserve page numbers (for PDF) and row numbers (for CSV/XLSX) in metadata.
- Handle multi-column PDFs and scanned PDFs (OCR fallback using `pytesseract` — optional, clearly marked).

### FR-03: Text Chunking
- Split extracted text into overlapping chunks.
- Default parameters: chunk size = 512 tokens, overlap = 50 tokens.
- Use LangChain's `RecursiveCharacterTextSplitter` as primary splitter.
- Preserve chunk metadata: `document_id`, `chunk_index`, `page_number`, `source_filename`, `char_start`, `char_end`.

### FR-04: Embedding Generation
- Generate dense vector embeddings for each chunk using `sentence-transformers/all-MiniLM-L6-v2`.
- Embed user query at query time using the same model.
- Support configurable embedding model via environment variable.

### FR-05: Vector Storage
- Store each chunk embedding along with metadata in the configured vector store.
- Support Qdrant (cloud free tier) as primary vector store.
- Support ChromaDB as local fallback (zero API key required).
- Store metadata fields: `document_id`, `chunk_index`, `text`, `source_filename`, `page_number`, `char_start`, `char_end`, `created_at`.

### FR-06: Semantic Retrieval
- On user query, embed the question and perform cosine similarity search.
- Retrieve top-k = 5 most relevant chunks by default (configurable).
- Filter retrieval by `document_id` to scope results to the active document.
- Return retrieved chunks with similarity scores.

### FR-07: LLM Answer Generation
- Send retrieved chunks as context + user question to the LLM.
- Use Groq API (Llama 3.1 8B or Mixtral 8x7B) as primary LLM.
- Use a structured prompt template (see Section 20).
- Return the generated answer as a string.
- Do not hallucinate content not present in retrieved context (instruction in system prompt).

### FR-08: Citation Construction
- Map each sentence or claim in the LLM answer back to source chunks where possible.
- Return a `citations` array in the API response with fields: `chunk_index`, `page_number`, `source_filename`, `excerpt` (first 200 chars of chunk), `similarity_score`.

### FR-09: Document Management
- `GET /documents` — list all ingested documents (session-scoped for MVP).
- `DELETE /documents/{document_id}` — delete document and its vectors.

### FR-10: Evaluation
- `POST /eval` — run RAGAS evaluation on a provided test dataset.
- Accept a JSON array of `{question, answer, contexts, ground_truth}` objects.
- Return scores for: `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`.

### FR-11: Health Check
- `GET /health` — return service status, version, vector store connection status, and LLM provider status.

---

## 9. Non-Functional Requirements

### NFR-01: Performance
- Upload + ingest (parse, chunk, embed, store) for a 10-page PDF: < 30 seconds.
- Query → answer latency: < 5 seconds (excluding first cold-start embedding model load).
- Embedding model cold-start: < 10 seconds (cached after first load).

### NFR-02: Reliability
- Graceful error handling on all endpoints — never return unstructured 500 errors.
- Retry logic (1 retry with 2s backoff) on Groq API calls.
- If vector DB is unavailable, return a meaningful error, not a crash.

### NFR-03: Scalability (Demo-Grade)
- Designed for 1–10 concurrent users during demos.
- No horizontal scaling required for MVP.
- Stateless API design to enable future scaling.

### NFR-04: Maintainability
- All configuration via environment variables (`.env` file, never hardcoded).
- Modular codebase: separate modules for parsing, chunking, embedding, retrieval, generation.
- Docstrings on all public functions.
- Type hints throughout.

### NFR-05: Portability
- All services runnable via `docker-compose up`.
- No platform-specific code.
- Works on Linux, macOS, and Windows (via Docker).

### NFR-06: Observability
- Structured JSON logging using Python `logging` + `python-json-logger`.
- Request ID propagation in logs.
- Log levels: DEBUG, INFO, WARNING, ERROR configurable via env var.

### NFR-07: Security (Demo-Grade)
- Input validation on all endpoints (Pydantic models).
- File type validation using magic bytes, not just file extension.
- Rate limiting: 10 requests/minute per IP (using `slowapi`).
- No sensitive data (API keys) committed to git.
- `.gitignore` covers `.env`, `__pycache__`, vector store data, uploaded files.

---

## 10. MVP Scope

The MVP must include the following and nothing more:

| Feature | Included in MVP |
|---|---|
| PDF upload and parsing | ✅ |
| DOCX upload and parsing | ✅ |
| TXT upload and parsing | ✅ |
| CSV upload and parsing | ✅ |
| Text chunking | ✅ |
| Embedding (local SentenceTransformers) | ✅ |
| ChromaDB local vector store | ✅ |
| Qdrant cloud vector store | ✅ (configurable) |
| Groq LLM integration | ✅ |
| REST API (FastAPI) | ✅ |
| Basic web UI | ✅ |
| Citations / chunk references | ✅ |
| RAGAS evaluation endpoint | ✅ |
| Docker + docker-compose | ✅ |
| README with screenshots | ✅ |
| Health check endpoint | ✅ |
| XLSX parsing | ⬜ (optional, documented) |
| Image upload + OCR | ⬜ (optional, documented) |
| Streaming LLM responses | ⬜ (Phase 2) |
| Multi-user auth | ⬜ (Phase 2) |
| Pinecone integration | ⬜ (alternative to Qdrant) |
| Conversation memory / chat history | ⬜ (Phase 2) |

---

## 11. Future Scope

| Feature | Priority |
|---|---|
| Streaming answers via SSE | High |
| Conversation history / multi-turn Q&A | High |
| User authentication (JWT) | High |
| Per-user document isolation | High |
| Re-ranking retrieved chunks (Cohere or cross-encoder) | Medium |
| Hybrid search (BM25 + dense) | Medium |
| Async background ingestion with job queue (Celery/ARQ) | Medium |
| Document summarization endpoint | Medium |
| Table extraction from PDFs | Medium |
| OpenAI / Anthropic LLM provider toggle | Low |
| Knowledge graph extraction | Low |
| Export answers to PDF/DOCX | Low |
| Admin dashboard for document/eval management | Low |

---

## 12. System Architecture

### Architecture Overview (Text Diagram)

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
│                                                             │
│   ┌─────────────────┐          ┌─────────────────────────┐  │
│   │   Web Browser   │          │   API Client / cURL /   │  │
│   │  (HTML/CSS/JS)  │          │   Swagger UI /docs      │  │
│   └────────┬────────┘          └───────────┬─────────────┘  │
└────────────┼──────────────────────────────┼────────────────┘
             │ HTTP/REST                     │ HTTP/REST
             ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                         │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  /upload │  │   /ask   │  │/documents│  │ /health  │   │
│  │  router  │  │  router  │  │  router  │  │  /eval   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘   │
│       │             │             │                         │
│       ▼             │             ▼                         │
│  ┌──────────────────┼──────────────────────────────────┐   │
│  │              PIPELINE LAYER                         │   │
│  │                  │                                  │   │
│  │  ┌─────────┐  ┌──▼──────┐  ┌───────────┐           │   │
│  │  │  File   │  │Retrieval│  │  LLM Gen  │           │   │
│  │  │ Parser  │  │ Engine  │  │  Engine   │           │   │
│  │  └────┬────┘  └────┬────┘  └─────┬─────┘           │   │
│  │       │            │             │                  │   │
│  │  ┌────▼────┐       │       ┌─────▼─────┐            │   │
│  │  │ Chunker │       │       │  Citation │            │   │
│  │  └────┬────┘       │       │  Builder  │            │   │
│  │       │            │       └───────────┘            │   │
│  │  ┌────▼────┐       │                                │   │
│  │  │Embedder │───────┘                                │   │
│  │  └─────────┘                                        │   │
│  └──────────────────────────────────────────────────── ┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                      │                    │
         ▼                      ▼                    ▼
┌─────────────┐      ┌──────────────────┐   ┌──────────────┐
│  LOCAL FILE │      │  VECTOR STORE    │   │  GROQ LLM    │
│   STORAGE   │      │                  │   │   API        │
│  /uploads/  │      │ ┌──────────────┐ │   │              │
│  (temp)     │      │ │  Qdrant Cloud│ │   │ Llama 3.1 8B │
└─────────────┘      │ │  (primary)   │ │   │  or Mixtral  │
                     │ └──────────────┘ │   └──────────────┘
                     │ ┌──────────────┐ │
                     │ │  ChromaDB    │ │
                     │ │  (fallback)  │ │
                     │ └──────────────┘ │
                     └──────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|---|---|
| **FastAPI Routers** | HTTP request/response, input validation, error formatting |
| **File Parser** | Text extraction from PDF/DOCX/TXT/CSV |
| **Chunker** | Split text into overlapping segments with metadata |
| **Embedder** | Generate dense vectors using SentenceTransformers |
| **Vector Store Adapter** | Abstract interface for Qdrant / ChromaDB |
| **Retrieval Engine** | Embed query, run similarity search, return top-k chunks |
| **LLM Engine** | Build prompt, call Groq API, parse response |
| **Citation Builder** | Map answer back to source chunks |
| **RAGAS Evaluator** | Run offline evaluation against test dataset |

---

## 13. Data Flow

### Ingestion Flow (Upload)

```
1. User uploads file via POST /upload
2. FastAPI validates: file type (magic bytes), file size
3. File saved to /tmp/uploads/{document_id}/
4. File Parser extracts raw text (+ page numbers for PDF)
5. Chunker splits text → List[Chunk]
   Each Chunk: {text, chunk_index, page_number, char_start, char_end}
6. Embedder generates vector for each Chunk.text
7. Vector Store Adapter upserts (vector, metadata) pairs
   Collection/namespace scoped by document_id
8. Document metadata saved to in-memory store (or SQLite for persistence)
9. API returns: {document_id, filename, chunk_count, status: "ready"}
```

### Query Flow (Ask)

```
1. User sends POST /ask {document_id, question}
2. FastAPI validates inputs
3. Embedder encodes question → query_vector
4. Vector Store Adapter runs similarity search:
   - Filter: document_id == {document_id}
   - Top-k: 5
   - Returns: List[{text, metadata, score}]
5. LLM Engine builds prompt:
   - System: "Answer using only the context provided..."
   - Context: concatenated chunk texts with [SOURCE N] markers
   - Question: user question
6. Groq API called → raw answer string
7. Citation Builder matches [SOURCE N] markers → citation objects
8. API returns: {answer, citations: [{chunk_index, page_number, excerpt, score}]}
```

---

## 14. API Requirements

### Base URL
- Local: `http://localhost:8000`
- Deployed: `https://{app-name}.onrender.com` (or similar)

### Authentication
- MVP: No authentication. Add API key header (`X-API-Key`) as Phase 2.
- Rate limiting: 10 req/min per IP via `slowapi`.

### Content Type
- Uploads: `multipart/form-data`
- All other requests/responses: `application/json`

### Standard Response Envelope

**Success:**
```json
{
  "status": "success",
  "data": { ... },
  "request_id": "uuid4"
}
```

**Error:**
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "File type .exe is not supported.",
    "detail": null
  },
  "request_id": "uuid4"
}
```

### Versioning
- All routes prefixed with `/api/v1/`.
- `/docs` → Swagger UI.
- `/redoc` → ReDoc.

---

## 15. UI Requirements

### UI Technology
- MVP: Single-page HTML + Tailwind CSS (CDN) + vanilla JavaScript.
- Served directly by FastAPI as static files at `/`.
- Optional: React SPA for Phase 2.

### Required Screens / States

#### Screen 1: Upload Screen
- Large drag-and-drop zone with dashed border.
- "Or click to browse" fallback.
- File type hint text: "PDF, DOCX, TXT, CSV — max 20MB".
- Upload progress bar (0–100%).
- Success state: "✅ Document ready — {filename} ({N} chunks indexed)".
- Error state: inline red error message.

#### Screen 2: Chat / Q&A Screen (shown after upload succeeds)
- Prominent "Ask a question" input box.
- Send button (also triggered by Enter key).
- Spinner while answer is generating.
- Answer display area with formatted text.
- Citations panel (collapsible) showing source chunks with page references.
- "Upload another document" link.

#### Screen 3: Document List (optional sidebar or modal)
- List of uploaded documents in current session.
- Delete button per document.
- Click to switch active document.

### UI Non-Requirements
- User accounts / login screens.
- Mobile-native gestures (responsive layout is fine).
- Dark mode (nice-to-have, not required for MVP).

### UI Polish Requirements (Portfolio Grade)
- Clean, modern look — inspired by ChatPDF / Perplexity aesthetic.
- System font stack or Google Fonts (Inter or DM Sans).
- Consistent spacing (8px grid).
- Loading skeletons on answer area.
- Answer text supports basic markdown rendering (bold, code blocks, lists).
- Footer: "Built with FastAPI · LangChain · Groq · Qdrant" with GitHub link.

---

## 16. File Upload Requirements

### Accepted File Types and Parsers

| Extension | MIME Type | Parser |
|---|---|---|
| `.pdf` | `application/pdf` | PyMuPDF (`fitz`) |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | `python-docx` |
| `.txt` | `text/plain` | Native Python `open()` |
| `.csv` | `text/csv` | `pandas.read_csv()` |
| `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `pandas.read_excel()` |

### Validation Rules
- **Type validation:** Check both file extension AND magic bytes (first 8 bytes of file).
  - PDF magic: `%PDF` (`25 50 44 46`)
  - DOCX/XLSX magic: `PK` (`50 4B`) — they're ZIP files
  - Fall back to extension check if magic bytes are inconclusive
- **Size limit:** 20MB maximum. Return HTTP 413 with error code `FILE_TOO_LARGE`.
- **Empty file:** Reject files with 0 bytes. Return HTTP 400 with error code `EMPTY_FILE`.
- **Password-protected PDF:** Detect and return HTTP 422 with error code `ENCRYPTED_FILE`.

### Storage
- Files stored temporarily at `/tmp/uploads/{document_id}/{original_filename}`.
- Files deleted after successful ingestion (do not persist raw files in production).
- For demo mode: optionally keep files for re-ingestion (env var `KEEP_UPLOADED_FILES=true`).

### Deduplication (MVP: Skip)
- Phase 2: Hash file content (SHA-256) and skip re-ingestion if hash already exists.

---

## 17. Document Parsing and Chunking Requirements

### PDF Parsing (PyMuPDF)

```python
# Pseudocode — implement in app/pipeline/parsers/pdf_parser.py
import fitz  # PyMuPDF

def parse_pdf(file_path: str) -> List[PageText]:
    doc = fitz.open(file_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")  # plain text extraction
        pages.append(PageText(page_number=page_num, text=text))
    return pages
```

- Use `"blocks"` mode for better layout preservation on multi-column PDFs.
- Fallback to `pypdf` if PyMuPDF fails (e.g., unusual encoding).
- Strip excessive whitespace and normalize newlines.

### DOCX Parsing

```python
from docx import Document

def parse_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
```

### Chunking

**Recommended Parameters:**
- `chunk_size`: 512 characters (not tokens — character-based for simplicity; maps to ~128 tokens for English text).
- `chunk_overlap`: 50 characters.
- Splitter: `RecursiveCharacterTextSplitter` with separators `["\n\n", "\n", " ", ""]`.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.create_documents(
    texts=[page.text for page in pages],
    metadatas=[{"page_number": page.page_number, "source": filename} for page in pages]
)
```

### Chunk Metadata Schema

```python
class ChunkMetadata(BaseModel):
    document_id: str          # UUID4
    chunk_index: int          # 0-based index within document
    page_number: int          # 1-based (0 if not applicable)
    source_filename: str      # original filename
    char_start: int           # character offset in source page text
    char_end: int             # character offset end
    created_at: str           # ISO 8601 timestamp
    text: str                 # the chunk text itself (stored in metadata for retrieval)
```

---

## 18. Embedding and Vector Database Requirements

### Embedding Model

**Primary:** `sentence-transformers/all-MiniLM-L6-v2`
- Embedding dimension: 384
- Free, runs locally, no API key.
- Runs on CPU comfortably for demo-scale documents.
- Download once on first run, cache via HuggingFace cache directory.

**Configurable via env var:** `EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`

**Alternative (larger model):** `sentence-transformers/all-mpnet-base-v2` (dimension: 768) — better quality, slower.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))

def embed_texts(texts: List[str]) -> List[List[float]]:
    return model.encode(texts, convert_to_numpy=True).tolist()
```

### Vector Database — Qdrant (Primary)

- Use **Qdrant Cloud Free Tier** (1 cluster, 1GB storage, no credit card).
- Collection name: `document_chunks`.
- Vector size: 384 (match embedding model).
- Distance metric: **Cosine**.
- Create one collection at startup; use `document_id` payload filter for isolation.

**Qdrant point schema:**
```python
{
    "id": str(uuid4()),          # unique point ID
    "vector": List[float],       # 384-dim embedding
    "payload": {
        "document_id": str,
        "chunk_index": int,
        "page_number": int,
        "source_filename": str,
        "char_start": int,
        "char_end": int,
        "created_at": str,
        "text": str              # chunk text for retrieval display
    }
}
```

### Vector Database — ChromaDB (Fallback)

- Pure Python, no API key, no server needed.
- Persist to `./data/chroma/` directory.
- Collection per document: `f"doc_{document_id}"`.
- Activated when `VECTOR_STORE=chroma` (env var).

### Vector Store Abstraction

Implement a `VectorStoreAdapter` abstract base class with methods:
- `upsert(points: List[VectorPoint]) -> None`
- `search(query_vector: List[float], document_id: str, top_k: int) -> List[SearchResult]`
- `delete_document(document_id: str) -> None`
- `health_check() -> bool`

Concrete implementations: `QdrantAdapter`, `ChromaAdapter`.

---

## 19. Retrieval Requirements

### Similarity Search

- Metric: Cosine similarity (Qdrant default for Cosine collections).
- Default top-k: **5** (configurable via env var `RETRIEVAL_TOP_K=5`).
- Minimum score threshold: **0.3** (discard irrelevant chunks). Configurable via `RETRIEVAL_MIN_SCORE=0.3`.
- Always filter by `document_id` to prevent cross-document contamination.

### Retrieval Output Schema

```python
class RetrievedChunk(BaseModel):
    chunk_index: int
    text: str
    page_number: int
    source_filename: str
    similarity_score: float
    char_start: int
    char_end: int
```

### Context Window Construction

After retrieval, sort chunks by `chunk_index` (document order, not score order) before sending to LLM. This preserves narrative coherence.

Format for LLM context:
```
[SOURCE 1] (Page 3)
{chunk_text_1}

[SOURCE 2] (Page 3)
{chunk_text_2}

[SOURCE 3] (Page 7)
{chunk_text_3}
```

---

## 20. LLM Answer Generation Requirements

### LLM Provider — Groq (Primary)

- API: `https://api.groq.com/openai/v1/chat/completions` (OpenAI-compatible).
- Model: `llama-3.1-8b-instant` (fast, free tier, high quality).
- Fallback model: `mixtral-8x7b-32768` (larger context window for long documents).
- Max tokens: 1024.
- Temperature: 0.1 (low, for factual/grounded responses).

### Prompt Template

```python
SYSTEM_PROMPT = """You are a precise document analysis assistant. Your task is to answer questions based ONLY on the provided document context.

Rules:
1. Answer using ONLY information from the context below. Do not use prior knowledge.
2. If the answer is not in the context, say "I cannot find this information in the provided document."
3. When you use information from a source, cite it inline as [SOURCE N] matching the source labels in the context.
4. Be concise but complete. Prefer bullet points for multi-part answers.
5. Never fabricate facts, numbers, names, or dates.
"""

HUMAN_PROMPT_TEMPLATE = """
Context from document "{filename}":

{context}

---

Question: {question}

Answer (cite sources as [SOURCE N]):
"""
```

### LangChain Integration

Use `langchain_groq.ChatGroq` or direct `groq` Python SDK. Implement in `app/pipeline/llm_engine.py`.

```python
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_answer(question: str, context_chunks: List[RetrievedChunk], filename: str) -> str:
    context = build_context_string(context_chunks)
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": HUMAN_PROMPT_TEMPLATE.format(
                filename=filename, context=context, question=question
            )}
        ],
        max_tokens=1024,
        temperature=0.1
    )
    return response.choices[0].message.content
```

### Retry Logic

- Retry on Groq API errors (429, 503) with exponential backoff: 1s, 2s, 4s (max 3 retries).
- Use `tenacity` library.

---

## 21. Citation and Source Reference Requirements

### Citation Format in API Response

```json
{
  "answer": "The company reported revenue of $4.2B in Q3 [SOURCE 1]. This was driven by growth in the cloud segment [SOURCE 2].",
  "citations": [
    {
      "source_label": "SOURCE 1",
      "chunk_index": 14,
      "page_number": 7,
      "source_filename": "annual_report_2024.pdf",
      "excerpt": "In Q3 2024, total revenue reached $4.2 billion, representing a 23% year-over-year increase...",
      "similarity_score": 0.89
    },
    {
      "source_label": "SOURCE 2",
      "chunk_index": 15,
      "page_number": 8,
      "source_filename": "annual_report_2024.pdf",
      "excerpt": "Cloud services revenue grew 41% driven by enterprise adoption of the core platform...",
      "similarity_score": 0.76
    }
  ],
  "model_used": "llama-3.1-8b-instant",
  "latency_ms": 2341,
  "chunks_retrieved": 5
}
```

### Citation Construction Logic

1. Parse the LLM answer for `[SOURCE N]` markers using regex: `\[SOURCE (\d+)\]`.
2. Map N-1 (0-based) to the Nth retrieved chunk in the ordered list.
3. Build citation object from chunk metadata.
4. Return only the citations that were actually referenced in the answer.

### UI Citation Display

- Numbered badges `[1]`, `[2]` inline in the answer text (hyperlinks to citation panel).
- Collapsible citation panel below the answer.
- Each citation card shows: filename, page number, similarity score, and truncated excerpt (200 chars).

---

## 22. Evaluation Requirements — RAGAS

### Purpose

RAGAS (RAG Assessment) provides automated metrics to evaluate the quality of the RAG pipeline without needing human annotators. These scores are documented in the README and used to demonstrate system quality.

### RAGAS Metrics

| Metric | What it Measures | Target |
|---|---|---|
| **Faithfulness** | Are all claims in the answer supported by the retrieved context? | ≥ 0.80 |
| **Answer Relevancy** | Is the answer relevant to the question? | ≥ 0.75 |
| **Context Precision** | Are the retrieved chunks actually relevant to the question? | ≥ 0.75 |
| **Context Recall** | Does the retrieved context contain all info needed to answer? | ≥ 0.70 |

### Evaluation Dataset

- A `tests/eval_dataset.json` file containing 10–20 question/answer pairs.
- Format:

```json
[
  {
    "question": "What was the total revenue in Q3 2024?",
    "answer": "The company reported total revenue of $4.2 billion in Q3 2024.",
    "contexts": ["In Q3 2024, total revenue reached $4.2 billion..."],
    "ground_truth": "Total revenue in Q3 2024 was $4.2 billion."
  }
]
```

### Evaluation Endpoint

**POST /api/v1/eval**

```json
// Request
{
  "document_id": "uuid4",
  "eval_dataset": [
    {"question": "...", "ground_truth": "..."}
  ]
}

// Response
{
  "status": "success",
  "data": {
    "faithfulness": 0.84,
    "answer_relevancy": 0.79,
    "context_precision": 0.81,
    "context_recall": 0.72,
    "num_samples": 15,
    "eval_model": "llama-3.1-8b-instant"
  }
}
```

### Offline Evaluation Script

Also provide `scripts/run_eval.py` for running evaluation from command line:

```bash
python scripts/run_eval.py \
  --document_id {uuid} \
  --eval_file tests/eval_dataset.json \
  --output eval_results.json
```

### RAGAS Dependencies

```
ragas>=0.1.0
datasets>=2.14.0
```

Note: RAGAS currently requires an OpenAI API key for its built-in LLM evaluator. Workaround: configure RAGAS to use a local model or Groq (documented in README with instructions).

---

## 23. Security and Privacy Requirements

### Input Validation
- All request bodies validated with Pydantic v2 models.
- File MIME type validated via magic bytes + extension.
- Question string: max 1000 characters, strip leading/trailing whitespace.
- `document_id`: validate UUID4 format before any DB lookup.

### File Security
- Never execute uploaded files.
- File stored in an isolated temp directory, not in the web root.
- Sanitize original filename before storage: replace spaces, remove `../`, limit to alphanumeric + common punctuation.

### API Key Security
- All API keys stored in environment variables, never in source code.
- `.env` in `.gitignore`.
- `.env.example` committed with placeholder values.

### Rate Limiting
- 10 requests/minute per IP using `slowapi` middleware.
- Configurable via `RATE_LIMIT_PER_MINUTE=10`.

### CORS
- In development: `CORS_ORIGINS=*`.
- In production: restrict to known frontend origin via `CORS_ORIGINS` env var.

### Demo-Grade Notes (Not True Production)
- No user authentication or session isolation in MVP.
- Uploaded documents are accessible to anyone who knows the `document_id`.
- For true production: add JWT authentication and per-user vector namespacing.

---

## 24. Error Handling Requirements

### Error Code Registry

| HTTP Status | Error Code | Trigger |
|---|---|---|
| 400 | `INVALID_REQUEST` | Malformed request body |
| 400 | `EMPTY_FILE` | Uploaded file has 0 bytes |
| 400 | `INVALID_QUESTION` | Question is empty or too long |
| 404 | `DOCUMENT_NOT_FOUND` | `document_id` not in store |
| 413 | `FILE_TOO_LARGE` | File exceeds 20MB |
| 415 | `INVALID_FILE_TYPE` | Unsupported file extension/MIME |
| 422 | `ENCRYPTED_FILE` | Password-protected PDF |
| 422 | `PARSE_FAILED` | Unable to extract text from file |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `LLM_UNAVAILABLE` | Groq API down or key invalid |
| 500 | `VECTOR_STORE_ERROR` | Qdrant/Chroma connection failed |
| 500 | `INTERNAL_ERROR` | Unhandled exception |

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size 24.3MB exceeds the 20MB limit.",
    "detail": {"file_size_mb": 24.3, "limit_mb": 20}
  },
  "request_id": "3f2c1b0a-..."
}
```

### FastAPI Exception Handlers

Register global exception handlers for:
- `RequestValidationError` → 422
- `HTTPException` → pass-through
- `Exception` → 500 with sanitized message (never expose stack traces in production)

---

## 25. Deployment Requirements

### Local Development

```bash
# Option 1: Docker Compose (recommended)
docker-compose up --build

# Option 2: Manual
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Requirements

**Dockerfile:**
- Base image: `python:3.11-slim`.
- Multi-stage build to keep image size small (< 1.5GB including model cache).
- Non-root user for security.
- HEALTHCHECK instruction pointing to `/api/v1/health`.
- Cache pip dependencies layer separately from app code.

**docker-compose.yml:**
```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    volumes:
      - ./data:/app/data          # ChromaDB persistence
      - ./uploads:/tmp/uploads    # temporary file storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Free Hosting Options

| Platform | Free Tier | Limitations | Recommended Use |
|---|---|---|---|
| **Render** | 512MB RAM, 0.1 CPU, spins down after inactivity | Slow cold start (~30s) | Primary recommendation |
| **Hugging Face Spaces** | 2 vCPU, 16GB RAM (on CPU tier) | No persistent disk | Best performance |
| **Railway** | $5 free credits/month | Credit-based, not always free | Good for temporary demos |
| **Fly.io** | 3 shared-CPU VMs, 256MB RAM | Very limited RAM | Not recommended (too little RAM for model) |

**Recommended: Hugging Face Spaces (Docker SDK)**
- Best free performance for ML workloads.
- Supports Docker deployment.
- Persistent storage add-on available.
- Public URL immediately.

### Deployment Steps for Render

1. Connect GitHub repo to Render.
2. Set environment variables in Render dashboard.
3. Set build command: `pip install -r requirements.txt`.
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Add `render.yaml` for infrastructure-as-code.

### `render.yaml`

```yaml
services:
  - type: web
    name: document-intelligence-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: VECTOR_STORE
        value: qdrant
      - key: GROQ_API_KEY
        sync: false
      - key: QDRANT_URL
        sync: false
      - key: QDRANT_API_KEY
        sync: false
```

---

## 26. Observability and Logging Requirements

### Logging

- Use Python `logging` module + `python-json-logger`.
- All logs output as structured JSON (one JSON object per line).
- Log level configurable via `LOG_LEVEL=INFO`.

**Log fields:**
```json
{
  "timestamp": "2026-06-02T10:23:45.123Z",
  "level": "INFO",
  "logger": "app.pipeline.embedder",
  "request_id": "uuid4",
  "message": "Generated embeddings for 47 chunks",
  "document_id": "uuid4",
  "chunk_count": 47,
  "duration_ms": 1230
}
```

### Key Log Events

| Event | Level | Fields |
|---|---|---|
| File uploaded | INFO | filename, size_bytes, document_id |
| Parsing complete | INFO | document_id, page_count, char_count |
| Chunking complete | INFO | document_id, chunk_count |
| Embedding complete | INFO | document_id, chunk_count, duration_ms |
| Vector upsert complete | INFO | document_id, point_count |
| Query received | INFO | document_id, question_length |
| Retrieval complete | INFO | document_id, chunks_retrieved, top_score |
| LLM call complete | INFO | model, input_tokens, output_tokens, duration_ms |
| Error | ERROR | error_code, message, traceback |

### Metrics (Optional for MVP)

- Add `prometheus-fastapi-instrumentator` for Prometheus metrics at `/metrics`.
- Track: request count, request latency, error rate.
- Not required for MVP, but adds impressive points to portfolio.

### Request ID Propagation

- Generate UUID4 `request_id` per request in middleware.
- Inject into all log lines for the request lifecycle.
- Return in API response headers as `X-Request-ID`.

---

## 27. README / GitHub Portfolio Requirements

The README is as important as the code for portfolio purposes. It must include:

### Required README Sections

1. **Project Title + Badges**
   - Build status badge, Python version badge, License badge, Demo link badge.

2. **One-Line Description**
   - "Upload any document. Ask it anything. Get cited answers."

3. **Live Demo Link**
   - Link to deployed app (Hugging Face Spaces / Render).

4. **Screenshot / GIF**
   - At minimum 2 screenshots: upload screen and answer with citations.
   - Animated GIF of the full user flow (optional but impressive).

5. **Architecture Diagram**
   - Copy the text architecture diagram from Section 12.
   - Or generate with `diagrams` Python library or draw.io and export as PNG.

6. **Tech Stack Table**
   - Clean table matching Section 1 stack summary.

7. **Features List**
   - Bullet list of key features.

8. **Quick Start (Local)**
   ```bash
   git clone https://github.com/{username}/document-intelligence-api
   cd document-intelligence-api
   cp .env.example .env
   # Fill in GROQ_API_KEY and QDRANT_* in .env
   docker-compose up --build
   # Visit http://localhost:8000
   ```

9. **Environment Variables Table**
   - All env vars from Section 33 documented with descriptions and defaults.

10. **API Documentation Summary**
    - Table of endpoints with method, path, description.
    - Link to `/docs` for full interactive docs.

11. **RAGAS Evaluation Scores**
    - Table of metric scores from latest evaluation run.
    - Document: "evaluated against {N} question-answer pairs on {sample_document_name}".

12. **Project Structure**
    - Copy from Section 31.

13. **Deployment Guide**
    - Render deployment steps.
    - Hugging Face Spaces steps.

14. **Development Guide**
    - How to run tests: `pytest`.
    - How to run linter: `ruff check .`.
    - How to run formatter: `black .`.

15. **License**
    - MIT License.

16. **Contact / Portfolio Link**
    - Developer name, LinkedIn, portfolio website.

---

## 28. Acceptance Criteria

### AC-01: Upload
- [ ] User can upload a PDF file up to 20MB.
- [ ] System returns a `document_id` within 30 seconds for a 10-page PDF.
- [ ] Uploading a `.exe` file returns HTTP 415 with error code `INVALID_FILE_TYPE`.
- [ ] Uploading a 21MB file returns HTTP 413 with error code `FILE_TOO_LARGE`.

### AC-02: Parsing and Chunking
- [ ] A 10-page PDF is split into at least 10 chunks.
- [ ] Each chunk has non-empty `text`, valid `page_number`, and valid `document_id`.
- [ ] A DOCX file is parsed and chunked without errors.
- [ ] A CSV file is parsed and chunked without errors.

### AC-03: Embedding and Storage
- [ ] Embeddings are generated for all chunks without errors.
- [ ] All chunks are stored in the vector database with correct metadata.
- [ ] `GET /api/v1/health` shows `vector_store: "healthy"`.

### AC-04: Query and Retrieval
- [ ] A relevant question returns at least 1 chunk with score > 0.5.
- [ ] Retrieval is scoped to the specified `document_id`.
- [ ] A question unrelated to the document returns chunks with score < 0.3 (filtered out).

### AC-05: LLM Answer
- [ ] Answer is returned within 5 seconds of query submission.
- [ ] Answer contains at least one `[SOURCE N]` citation for a factual question.
- [ ] Answer for a question not covered by the document contains "cannot find this information".
- [ ] Answer does not contain information not in the retrieved context (verified manually for 3 test cases).

### AC-06: Citations
- [ ] API response contains `citations` array.
- [ ] Each citation has: `chunk_index`, `page_number`, `source_filename`, `excerpt`.
- [ ] UI displays citations in a collapsible panel below the answer.

### AC-07: RAGAS Evaluation
- [ ] `POST /api/v1/eval` returns valid metric scores (all between 0 and 1).
- [ ] Faithfulness ≥ 0.80 on the provided eval dataset.
- [ ] Results are logged and optionally saved to a file.

### AC-08: Docker
- [ ] `docker-compose up --build` starts the app without errors.
- [ ] App is accessible at `http://localhost:8000` after `docker-compose up`.
- [ ] `docker-compose down` stops all services cleanly.

### AC-09: README
- [ ] README contains live demo link, screenshots, stack table, and quick start guide.
- [ ] RAGAS evaluation scores are present in README.
- [ ] `.env.example` is present and complete.

### AC-10: Code Quality
- [ ] `pytest` runs with ≥ 70% pass rate.
- [ ] No hardcoded API keys in any tracked file.
- [ ] `ruff check .` returns 0 errors.

---

## 29. Technical Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Groq free tier rate limits hit during demo | Medium | High | Implement retry + exponential backoff. Cache answers for repeated questions. Fallback to OpenAI-compatible local model (Ollama). |
| Qdrant free tier goes down during demo | Low | High | ChromaDB local fallback. Toggle via `VECTOR_STORE=chroma`. |
| SentenceTransformer model download fails in Docker | Medium | High | Copy model into Docker image at build time using `sentence-transformers` download script. |
| PyMuPDF fails on unusual PDF encoding | Medium | Medium | Fallback to `pypdf`. Log the failure. Return partial result if possible. |
| Render free tier sleeps between requests | High | Medium | Add a UptimeRobot ping every 14 minutes. Or use HuggingFace Spaces instead. |
| RAGAS requires OpenAI key | High | Medium | Document workaround: use Groq-compatible RAGAS config or run evaluation with `ragas` custom LLM. |
| Large documents exceed free tier storage | Medium | Low | Enforce 20MB upload limit. Qdrant free tier has 1GB storage — sufficient for demo. |
| Cold start takes > 30s (embedding model load) | High | Medium | Pre-warm the embedding model at server startup in `app/main.py` lifespan event. |
| Docker image too large for Render free tier | Medium | Medium | Use multi-stage build, `python:3.11-slim`, and `.dockerignore`. |
| ChromaDB not thread-safe under concurrency | Low | Medium | Use `allow_reset=True` in single-threaded mode. For multi-user: use Qdrant. |

---

## 30. Suggested Milestones

### Milestone 1 — Foundation (Days 1–2)
- [ ] Initialize repo with folder structure from Section 31.
- [ ] FastAPI app skeleton (`app/main.py`) with `/health` and `/docs`.
- [ ] Pydantic models for all request/response schemas.
- [ ] Docker + docker-compose working.
- [ ] `.env.example` and logging setup.

### Milestone 2 — Ingestion Pipeline (Days 3–5)
- [ ] PDF parser (`PyMuPDF`).
- [ ] DOCX parser (`python-docx`).
- [ ] TXT and CSV parsers.
- [ ] `RecursiveCharacterTextSplitter` chunker.
- [ ] `SentenceTransformer` embedder.
- [ ] ChromaDB adapter (local fallback).
- [ ] `POST /api/v1/upload` endpoint end-to-end.
- [ ] Unit tests for parser and chunker.

### Milestone 3 — Query Pipeline (Days 6–8)
- [ ] Qdrant adapter.
- [ ] Retrieval engine (embed query, similarity search, filter by document_id).
- [ ] LLM engine (Groq integration, prompt template).
- [ ] Citation builder.
- [ ] `POST /api/v1/ask` endpoint end-to-end.
- [ ] `GET /api/v1/documents` endpoint.
- [ ] `DELETE /api/v1/documents/{document_id}` endpoint.
- [ ] Integration tests for full upload → ask flow.

### Milestone 4 — UI (Days 9–10)
- [ ] Static HTML/CSS/JS frontend.
- [ ] Upload screen with drag-and-drop.
- [ ] Chat screen with answer display.
- [ ] Citation panel (collapsible).
- [ ] Served by FastAPI at `/`.

### Milestone 5 — Evaluation and Polish (Days 11–12)
- [ ] RAGAS evaluation endpoint (`POST /api/v1/eval`).
- [ ] Evaluation script (`scripts/run_eval.py`).
- [ ] Sample eval dataset (`tests/eval_dataset.json`).
- [ ] Run evaluation, document scores in README.
- [ ] Rate limiting middleware.
- [ ] Error handling audit (all edge cases covered).

### Milestone 6 — Deployment and Documentation (Days 13–14)
- [ ] Deploy to Hugging Face Spaces or Render.
- [ ] README complete with screenshots, demo link, RAGAS scores.
- [ ] `CONTRIBUTING.md` and `LICENSE`.
- [ ] Final test run end-to-end on deployed URL.
- [ ] GitHub topics: `rag`, `langchain`, `fastapi`, `llm`, `vector-database`, `groq`, `nlp`.

---

## 31. Recommended Folder Structure

```
document-intelligence-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app factory, lifespan, middleware
│   ├── config.py                  # Settings class (pydantic-settings), loads .env
│   ├── dependencies.py            # FastAPI dependency injection (get_vector_store, etc.)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Aggregates all v1 routers
│   │       ├── upload.py          # POST /upload
│   │       ├── query.py           # POST /ask
│   │       ├── documents.py       # GET/DELETE /documents
│   │       ├── health.py          # GET /health
│   │       └── eval.py            # POST /eval
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py            # Pydantic request models
│   │   └── responses.py           # Pydantic response models
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── parsers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # BaseParser abstract class
│   │   │   ├── pdf_parser.py      # PyMuPDF + pypdf fallback
│   │   │   ├── docx_parser.py     # python-docx
│   │   │   ├── txt_parser.py      # plain text
│   │   │   ├── csv_parser.py      # pandas
│   │   │   └── factory.py         # get_parser(extension) factory function
│   │   │
│   │   ├── chunker.py             # RecursiveCharacterTextSplitter wrapper
│   │   ├── embedder.py            # SentenceTransformer wrapper, lazy singleton
│   │   ├── llm_engine.py          # Groq API client, prompt builder, retry logic
│   │   ├── citation_builder.py    # Map [SOURCE N] → chunk metadata
│   │   └── ingestion.py           # Orchestrates parse → chunk → embed → store
│   │
│   ├── vectorstore/
│   │   ├── __init__.py
│   │   ├── base.py                # VectorStoreAdapter ABC
│   │   ├── qdrant_adapter.py      # Qdrant implementation
│   │   ├── chroma_adapter.py      # ChromaDB implementation
│   │   └── factory.py             # get_vector_store() based on VECTOR_STORE env var
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_service.py    # Business logic: upload flow, query flow
│   │   └── eval_service.py        # RAGAS evaluation orchestration
│   │
│   └── utils/
│       ├── __init__.py
│       ├── file_validator.py      # Magic bytes + extension validation
│       ├── logging.py             # Logger factory, JSON formatter
│       └── exceptions.py          # Custom exception classes
│
├── frontend/
│   ├── index.html                 # Main SPA
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Fixtures: test client, mock vector store
│   ├── unit/
│   │   ├── test_pdf_parser.py
│   │   ├── test_chunker.py
│   │   ├── test_embedder.py
│   │   └── test_citation_builder.py
│   ├── integration/
│   │   ├── test_upload_flow.py
│   │   └── test_query_flow.py
│   ├── fixtures/
│   │   ├── sample.pdf
│   │   ├── sample.docx
│   │   └── sample.csv
│   └── eval_dataset.json          # RAGAS evaluation Q&A pairs
│
├── scripts/
│   ├── run_eval.py                # CLI: run RAGAS evaluation
│   ├── seed_demo.py               # Upload sample doc + ask sample questions
│   └── download_model.py          # Pre-download SentenceTransformer model
│
├── data/
│   └── chroma/                    # ChromaDB persistence (gitignored)
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions: lint + test on push
│
├── Dockerfile
├── docker-compose.yml
├── docker-compose.override.yml    # Local dev overrides (volumes, hot reload)
├── .env.example
├── .env                           # gitignored
├── .gitignore
├── .dockerignore
├── requirements.txt
├── requirements-dev.txt           # pytest, ruff, black, httpx
├── pyproject.toml                 # Tool config: ruff, black, pytest
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## 32. Example API Endpoints

### POST /api/v1/upload

**Request:**
```
Content-Type: multipart/form-data
Body: file=@annual_report.pdf
```

**Response 200:**
```json
{
  "status": "success",
  "data": {
    "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "filename": "annual_report.pdf",
    "file_size_bytes": 2457600,
    "page_count": 47,
    "chunk_count": 183,
    "status": "ready",
    "ingested_at": "2026-06-02T10:23:45.123Z"
  },
  "request_id": "req_xyz"
}
```

**Response 415:**
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "File type '.exe' is not supported. Accepted types: pdf, docx, txt, csv, xlsx.",
    "detail": {"received_type": ".exe", "accepted_types": ["pdf", "docx", "txt", "csv", "xlsx"]}
  },
  "request_id": "req_xyz"
}
```

---

### POST /api/v1/ask

**Request:**
```json
{
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "question": "What was the total revenue in Q3 2024?",
  "top_k": 5
}
```

**Response 200:**
```json
{
  "status": "success",
  "data": {
    "answer": "According to the document, total revenue in Q3 2024 was $4.2 billion, representing a 23% year-over-year increase [SOURCE 1]. This growth was primarily attributed to strong performance in the cloud services segment [SOURCE 2].",
    "citations": [
      {
        "source_label": "SOURCE 1",
        "chunk_index": 42,
        "page_number": 12,
        "source_filename": "annual_report.pdf",
        "excerpt": "In Q3 2024, total revenue reached $4.2 billion, representing a 23% year-over-year increase driven by...",
        "similarity_score": 0.91
      },
      {
        "source_label": "SOURCE 2",
        "chunk_index": 43,
        "page_number": 12,
        "source_filename": "annual_report.pdf",
        "excerpt": "Cloud services revenue grew 41% year-over-year, accounting for 38% of total Q3 revenue...",
        "similarity_score": 0.84
      }
    ],
    "model_used": "llama-3.1-8b-instant",
    "chunks_retrieved": 5,
    "latency_ms": 2103
  },
  "request_id": "req_abc"
}
```

---

### GET /api/v1/documents

**Response 200:**
```json
{
  "status": "success",
  "data": {
    "documents": [
      {
        "document_id": "a1b2c3d4-...",
        "filename": "annual_report.pdf",
        "chunk_count": 183,
        "page_count": 47,
        "file_size_bytes": 2457600,
        "ingested_at": "2026-06-02T10:23:45.123Z"
      }
    ],
    "total": 1
  },
  "request_id": "req_def"
}
```

---

### DELETE /api/v1/documents/{document_id}

**Response 200:**
```json
{
  "status": "success",
  "data": {
    "document_id": "a1b2c3d4-...",
    "deleted_chunks": 183,
    "message": "Document and all associated vectors deleted."
  },
  "request_id": "req_ghi"
}
```

---

### GET /api/v1/health

**Response 200:**
```json
{
  "status": "success",
  "data": {
    "service": "document-intelligence-api",
    "version": "1.0.0",
    "status": "healthy",
    "components": {
      "vector_store": {
        "type": "qdrant",
        "status": "healthy",
        "latency_ms": 45
      },
      "llm_provider": {
        "type": "groq",
        "status": "healthy",
        "model": "llama-3.1-8b-instant"
      },
      "embedding_model": {
        "type": "sentence-transformers",
        "model": "all-MiniLM-L6-v2",
        "status": "loaded",
        "dimension": 384
      }
    },
    "uptime_seconds": 3612
  }
}
```

---

### POST /api/v1/eval

**Request:**
```json
{
  "document_id": "a1b2c3d4-...",
  "eval_dataset": [
    {
      "question": "What was total Q3 revenue?",
      "ground_truth": "Total Q3 2024 revenue was $4.2 billion."
    },
    {
      "question": "Who is the CEO?",
      "ground_truth": "The CEO is Jane Smith."
    }
  ]
}
```

**Response 200:**
```json
{
  "status": "success",
  "data": {
    "faithfulness": 0.84,
    "answer_relevancy": 0.79,
    "context_precision": 0.81,
    "context_recall": 0.72,
    "num_samples": 2,
    "eval_model": "llama-3.1-8b-instant",
    "evaluated_at": "2026-06-02T10:30:00.000Z"
  },
  "request_id": "req_jkl"
}
```

---

## 33. Example Environment Variables

```bash
# .env.example — copy to .env and fill in your values

# ─── Application ─────────────────────────────────────────────
APP_NAME=document-intelligence-api
APP_VERSION=1.0.0
ENVIRONMENT=development           # development | production
LOG_LEVEL=INFO                    # DEBUG | INFO | WARNING | ERROR

# ─── Server ──────────────────────────────────────────────────
HOST=0.0.0.0
PORT=8000
RELOAD=true                       # Set false in production

# ─── CORS ────────────────────────────────────────────────────
CORS_ORIGINS=*                    # In production: https://yourdomain.com

# ─── File Upload ─────────────────────────────────────────────
MAX_FILE_SIZE_MB=20
UPLOAD_DIR=/tmp/uploads
KEEP_UPLOADED_FILES=false         # Set true for demo to allow re-ingestion

# ─── Chunking ────────────────────────────────────────────────
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# ─── Embedding Model ─────────────────────────────────────────
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_CACHE_DIR=/app/model_cache

# ─── Vector Store ────────────────────────────────────────────
VECTOR_STORE=qdrant               # qdrant | chroma

# Qdrant Cloud (get free at cloud.qdrant.io)
QDRANT_URL=https://xxxx.us-east-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=document_chunks

# ChromaDB (local fallback — no API key needed)
CHROMA_PERSIST_DIR=./data/chroma

# ─── Retrieval ───────────────────────────────────────────────
RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.3

# ─── LLM Provider ────────────────────────────────────────────
LLM_PROVIDER=groq                 # groq (only option in MVP)
GROQ_API_KEY=your_groq_api_key_here   # Get free at console.groq.com
GROQ_MODEL=llama-3.1-8b-instant   # or mixtral-8x7b-32768
LLM_MAX_TOKENS=1024
LLM_TEMPERATURE=0.1

# ─── Rate Limiting ───────────────────────────────────────────
RATE_LIMIT_PER_MINUTE=10

# ─── Evaluation ──────────────────────────────────────────────
EVAL_OUTPUT_DIR=./eval_results
```

---

## 34. Definition of Done

A feature is **Done** when all of the following are true:

1. **Code complete:** Feature is implemented per the functional requirements in this PRD.
2. **Tests pass:** Relevant unit and/or integration tests written and passing.
3. **Error handling:** All expected error cases handled with correct HTTP status codes and error codes.
4. **Logging:** Key events logged with appropriate log level and structured fields.
5. **Documented:** Public functions have docstrings. New env vars are in `.env.example`.
6. **Linted:** `ruff check .` passes with 0 errors.
7. **Docker verified:** Feature works inside `docker-compose up`.
8. **Acceptance criteria met:** All AC items for the feature are checked off.

The **project as a whole** is Done when:

1. All MVP features in Section 10 are implemented and their ACs are met.
2. `docker-compose up` results in a working app at `http://localhost:8000`.
3. The app is deployed publicly with a working URL.
4. README is complete with demo link, screenshots, and RAGAS scores.
5. RAGAS evaluation scores meet the targets in Section 5.
6. No API keys are present in the git history.
7. GitHub repo has appropriate description, topics, and license.

---

## 35. MVP Step-by-Step Checklist

Follow this checklist in order. Each item should be completable in < 2 hours.

### Phase 1: Scaffold

- [ ] `git init document-intelligence-api && cd document-intelligence-api`
- [ ] Create folder structure from Section 31
- [ ] `pip install fastapi uvicorn pydantic pydantic-settings python-dotenv`
- [ ] `app/config.py` — Settings class loading all env vars from Section 33
- [ ] `app/main.py` — FastAPI app with lifespan, CORS, static files mount
- [ ] `app/utils/logging.py` — JSON logger setup
- [ ] `app/utils/exceptions.py` — Custom exception classes + FastAPI handlers
- [ ] `app/api/v1/health.py` — GET /api/v1/health (returns static healthy)
- [ ] `Dockerfile` + `docker-compose.yml`
- [ ] `.env.example` + `.gitignore`
- [ ] Verify: `docker-compose up` → 200 on /api/v1/health

### Phase 2: Parsers

- [ ] `pip install pymupdf pypdf python-docx pandas openpyxl`
- [ ] `app/pipeline/parsers/base.py` — BaseParser ABC
- [ ] `app/pipeline/parsers/pdf_parser.py` — PyMuPDF implementation
- [ ] `app/pipeline/parsers/docx_parser.py`
- [ ] `app/pipeline/parsers/txt_parser.py`
- [ ] `app/pipeline/parsers/csv_parser.py`
- [ ] `app/pipeline/parsers/factory.py` — `get_parser(extension)`
- [ ] `app/utils/file_validator.py` — magic bytes + extension validation
- [ ] `tests/unit/test_pdf_parser.py` — test with `tests/fixtures/sample.pdf`
- [ ] `tests/unit/test_chunker.py`
- [ ] Verify: parse sample.pdf → get list of page texts

### Phase 3: Chunking + Embedding

- [ ] `pip install langchain langchain-text-splitters sentence-transformers`
- [ ] `app/pipeline/chunker.py` — RecursiveCharacterTextSplitter wrapper
- [ ] `app/pipeline/embedder.py` — SentenceTransformer singleton, `embed_texts()`
- [ ] `scripts/download_model.py` — pre-download model to cache dir
- [ ] Verify: chunk a PDF → get List[Document] with metadata
- [ ] Verify: embed 10 chunks → get 10 x 384 vectors

### Phase 4: Vector Store

- [ ] `pip install chromadb qdrant-client`
- [ ] `app/vectorstore/base.py` — VectorStoreAdapter ABC
- [ ] `app/vectorstore/chroma_adapter.py`
- [ ] `app/vectorstore/qdrant_adapter.py`
- [ ] `app/vectorstore/factory.py` — `get_vector_store()` reads VECTOR_STORE env var
- [ ] Verify ChromaDB: upsert 10 vectors, search returns correct top-k
- [ ] Set up Qdrant Cloud free account at cloud.qdrant.io
- [ ] Verify Qdrant: upsert 10 vectors, search returns correct top-k

### Phase 5: Upload Endpoint

- [ ] `app/pipeline/ingestion.py` — orchestrates parse → chunk → embed → store
- [ ] `app/models/requests.py` — UploadResponse model
- [ ] `app/models/responses.py` — DocumentResponse model
- [ ] `app/services/document_service.py` — document metadata store (in-memory dict)
- [ ] `app/api/v1/upload.py` — POST /api/v1/upload
- [ ] `app/api/v1/documents.py` — GET /api/v1/documents + DELETE
- [ ] `tests/integration/test_upload_flow.py`
- [ ] Verify: upload sample.pdf → 200 with document_id + chunk_count
- [ ] Verify: GET /api/v1/documents shows the uploaded document
- [ ] Update /health to check vector store connection

### Phase 6: Query Endpoint

- [ ] `pip install groq tenacity`
- [ ] `app/pipeline/llm_engine.py` — Groq client, prompt template, retry
- [ ] `app/pipeline/citation_builder.py` — parse [SOURCE N] → citations
- [ ] `app/api/v1/query.py` — POST /api/v1/ask
- [ ] `tests/integration/test_query_flow.py`
- [ ] `pip install slowapi` → add rate limiting middleware
- [ ] Verify: ask a question about uploaded doc → get answer + citations
- [ ] Verify: ask unrelated question → "cannot find this information"

### Phase 7: Frontend UI

- [ ] `frontend/index.html` — full SPA with Tailwind CSS CDN
- [ ] `frontend/js/app.js` — upload + query JavaScript logic
- [ ] Mount frontend as static files in `app/main.py`
- [ ] Verify: open http://localhost:8000 → see upload screen
- [ ] Verify: upload PDF in UI → see success state
- [ ] Verify: ask question in UI → see answer + citations panel

### Phase 8: Evaluation

- [ ] `pip install ragas datasets`
- [ ] `tests/eval_dataset.json` — 10+ Q&A pairs
- [ ] `app/services/eval_service.py` — RAGAS orchestration
- [ ] `app/api/v1/eval.py` — POST /api/v1/eval
- [ ] `scripts/run_eval.py` — CLI evaluation runner
- [ ] Run evaluation: `python scripts/run_eval.py --document_id {id} --eval_file tests/eval_dataset.json`
- [ ] Verify: all 4 RAGAS metrics returned and meet targets

### Phase 9: Polish + Tests

- [ ] `pip install python-json-logger` → structured JSON logging throughout
- [ ] Add request ID middleware
- [ ] Audit all error paths — ensure no unhandled 500s
- [ ] `requirements.txt` finalized (pin versions)
- [ ] `requirements-dev.txt`: pytest, httpx, ruff, black
- [ ] `pyproject.toml`: ruff + black config
- [ ] Run `ruff check . --fix`
- [ ] Run `pytest` — achieve ≥ 70% pass rate
- [ ] Final `docker-compose up --build` → full end-to-end test

### Phase 10: Deployment + README

- [ ] Create Hugging Face Space (Docker SDK) or Render service
- [ ] Set all env vars in deployment dashboard
- [ ] Push to GitHub, trigger deployment
- [ ] Verify live demo URL is working end-to-end
- [ ] Take 2–3 screenshots of working UI
- [ ] Run RAGAS eval against deployed instance, record scores
- [ ] Write README per Section 27 requirements
- [ ] Add GitHub topics: `rag`, `langchain`, `fastapi`, `llm`, `groq`, `qdrant`, `vector-database`, `python`
- [ ] Add demo link badge to README
- [ ] Final review: no secrets in git history (`git log --all -S "sk-"` check)
- [ ] Share GitHub repo URL 🎉

---

*End of Document — Document Intelligence API PRD v1.0.0*
