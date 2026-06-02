import uuid
from fastapi import APIRouter, Request, Depends

from app.models.responses import APIResponse, DocumentListData, DeleteData, DocumentInfo
from app.services.document_service import DocumentService, get_document_service
from app.utils.exceptions import DocumentNotFoundError

router = APIRouter()


@router.get("/documents", response_model=APIResponse)
async def list_documents(
    request: Request,
    doc_service: DocumentService = Depends(get_document_service),
):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    docs = doc_service.list_documents()
    data = DocumentListData(
        documents=[DocumentInfo(**d) for d in docs],
        total=len(docs),
    )
    return APIResponse(status="success", data=data, request_id=request_id)


@router.delete("/documents/{document_id}", response_model=APIResponse)
async def delete_document(
    document_id: str,
    request: Request,
    doc_service: DocumentService = Depends(get_document_service),
):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    try:
        uuid.UUID(document_id, version=4)
    except ValueError:
        raise DocumentNotFoundError(document_id)

    deleted_chunks = await doc_service.delete_document(document_id)
    data = DeleteData(
        document_id=document_id,
        deleted_chunks=deleted_chunks,
        message="Document and all associated vectors deleted.",
    )
    return APIResponse(status="success", data=data, request_id=request_id)
