import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Request, Depends

from app.models.responses import APIResponse, UploadData
from app.services.document_service import DocumentService, get_document_service
from app.utils.file_validator import validate_file, sanitize_filename
from app.utils.exceptions import EmptyFileError
from app.config import get_settings
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload", response_model=APIResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    doc_service: DocumentService = Depends(get_document_service),
):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    settings = get_settings()

    content = await file.read()
    filename = sanitize_filename(file.filename or "upload")

    # Validate (raises on error)
    validate_file(filename, content, settings.max_file_size_bytes)

    logger.info("File uploaded", extra={
        "request_id": request_id,
        "doc_filename": filename,
        "size_bytes": len(content),
    })

    result = await doc_service.ingest_document(
        content=content,
        filename=filename,
        request_id=request_id,
    )

    data = UploadData(
        document_id=result["document_id"],
        filename=result["filename"],
        file_size_bytes=result["file_size_bytes"],
        page_count=result["page_count"],
        chunk_count=result["chunk_count"],
        status="ready",
        ingested_at=result["ingested_at"],
    )

    return APIResponse(status="success", data=data, request_id=request_id)
