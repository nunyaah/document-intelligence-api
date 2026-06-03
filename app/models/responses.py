from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    detail: Any = None


class APIResponse(BaseModel):
    status: str  # "success" | "error"
    data: Any = None
    error: ErrorDetail | None = None
    request_id: str = ""


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    page_count: int
    file_size_bytes: int
    ingested_at: str


class UploadData(BaseModel):
    document_id: str
    filename: str
    file_size_bytes: int
    page_count: int
    chunk_count: int
    status: str = "ready"
    ingested_at: str


class Citation(BaseModel):
    source_label: str
    chunk_index: int
    page_number: int
    source_filename: str
    excerpt: str
    similarity_score: float


class AskData(BaseModel):
    answer: str
    citations: list[Citation]
    model_used: str
    chunks_retrieved: int
    latency_ms: int


class DocumentListData(BaseModel):
    documents: list[DocumentInfo]
    total: int


class DeleteData(BaseModel):
    document_id: str
    deleted_chunks: int
    message: str


class ComponentStatus(BaseModel):
    type: str
    status: str
    latency_ms: int | None = None
    model: str | None = None
    dimension: int | None = None


class HealthData(BaseModel):
    service: str
    version: str
    status: str
    components: dict[str, ComponentStatus]
    uptime_seconds: float


class EvalData(BaseModel):
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float
    num_samples: int
    eval_model: str
    evaluated_at: str
