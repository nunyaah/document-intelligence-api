import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

from app.config import get_settings
from app.utils.logging import setup_logging, get_logger
from app.utils.exceptions import (
    DocumentIntelligenceError,
    document_intelligence_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.api.v1.router import router as v1_router

settings = get_settings()
setup_logging()
logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm embedding model at startup to avoid cold-start penalty on first request
    logger.info("Starting up — pre-warming embedding model")
    try:
        from app.pipeline.embedder import get_embedder
        get_embedder()
        logger.info("Embedding model loaded")
    except Exception as exc:
        logger.warning("Could not pre-warm embedding model", extra={"error": str(exc)})

    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Ensure eval output directory exists
    os.makedirs(settings.eval_output_dir, exist_ok=True)

    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Document Intelligence API",
    description="Upload documents, ask natural language questions, get cited answers.",
    version=settings.app_version,
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


app.add_middleware(RequestIDMiddleware)

# Exception handlers
app.add_exception_handler(DocumentIntelligenceError, document_intelligence_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# API routes
app.include_router(v1_router)

# Frontend static files
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/static", StaticFiles(directory=_frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(_frontend_dir, "index.html"))
