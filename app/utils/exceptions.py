from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class DocumentIntelligenceError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, detail: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class InvalidFileTypeError(DocumentIntelligenceError):
    def __init__(self, received: str, accepted: list[str]):
        super().__init__(
            code="INVALID_FILE_TYPE",
            message=f"File type '{received}' is not supported. Accepted types: {', '.join(accepted)}.",
            status_code=415,
            detail={"received_type": received, "accepted_types": accepted},
        )


class FileTooLargeError(DocumentIntelligenceError):
    def __init__(self, size_mb: float, limit_mb: int):
        super().__init__(
            code="FILE_TOO_LARGE",
            message=f"File size {size_mb:.1f}MB exceeds the {limit_mb}MB limit.",
            status_code=413,
            detail={"file_size_mb": round(size_mb, 2), "limit_mb": limit_mb},
        )


class EmptyFileError(DocumentIntelligenceError):
    def __init__(self):
        super().__init__(code="EMPTY_FILE", message="Uploaded file is empty.", status_code=400)


class EncryptedFileError(DocumentIntelligenceError):
    def __init__(self):
        super().__init__(
            code="ENCRYPTED_FILE",
            message="The PDF is password-protected and cannot be processed.",
            status_code=422,
        )


class ParseFailedError(DocumentIntelligenceError):
    def __init__(self, filename: str, reason: str = ""):
        super().__init__(
            code="PARSE_FAILED",
            message=f"Unable to extract text from '{filename}'. {reason}".strip(),
            status_code=422,
        )


class DocumentNotFoundError(DocumentIntelligenceError):
    def __init__(self, document_id: str):
        super().__init__(
            code="DOCUMENT_NOT_FOUND",
            message=f"Document '{document_id}' not found.",
            status_code=404,
        )


class InvalidQuestionError(DocumentIntelligenceError):
    def __init__(self, reason: str = ""):
        super().__init__(
            code="INVALID_QUESTION",
            message=f"Question is invalid. {reason}".strip(),
            status_code=400,
        )


class LLMUnavailableError(DocumentIntelligenceError):
    def __init__(self, reason: str = ""):
        super().__init__(
            code="LLM_UNAVAILABLE",
            message=f"LLM provider is unavailable. {reason}".strip(),
            status_code=500,
        )


class VectorStoreError(DocumentIntelligenceError):
    def __init__(self, reason: str = ""):
        super().__init__(
            code="VECTOR_STORE_ERROR",
            message=f"Vector store error. {reason}".strip(),
            status_code=500,
        )


def _error_response(request: Request, status_code: int, code: str, message: str, detail=None) -> JSONResponse:
    import uuid
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "error": {"code": code, "message": message, "detail": detail},
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


async def document_intelligence_exception_handler(request: Request, exc: DocumentIntelligenceError) -> JSONResponse:
    return _error_response(request, exc.status_code, exc.code, exc.message, exc.detail)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return _error_response(request, 422, "INVALID_REQUEST", "Request validation failed.", exc.errors())


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    import logging
    logging.getLogger(__name__).exception("Unhandled exception")
    return _error_response(request, 500, "INTERNAL_ERROR", "An internal server error occurred.")
