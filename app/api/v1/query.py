import uuid
import time
from fastapi import APIRouter, Request, Depends

from app.models.requests import AskRequest
from app.models.responses import APIResponse, AskData, Citation
from app.services.document_service import DocumentService, get_document_service
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/ask", response_model=APIResponse)
async def ask_question(
    body: AskRequest,
    request: Request,
    doc_service: DocumentService = Depends(get_document_service),
):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    t0 = time.time()

    logger.info("Query received", extra={
        "request_id": request_id,
        "document_id": body.document_id,
        "question_length": len(body.question),
    })

    result = await doc_service.query_document(
        document_id=body.document_id,
        question=body.question,
        top_k=body.top_k,
        request_id=request_id,
    )

    citations = [
        Citation(
            source_label=c["source_label"],
            chunk_index=c["chunk_index"],
            page_number=c["page_number"],
            source_filename=c["source_filename"],
            excerpt=c["excerpt"],
            similarity_score=c["similarity_score"],
        )
        for c in result["citations"]
    ]

    data = AskData(
        answer=result["answer"],
        citations=citations,
        model_used=result["model_used"],
        chunks_retrieved=result["chunks_retrieved"],
        latency_ms=int((time.time() - t0) * 1000),
    )

    return APIResponse(status="success", data=data, request_id=request_id)
