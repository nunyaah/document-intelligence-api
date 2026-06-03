import time
import uuid

from fastapi import APIRouter, Request

from app.config import get_settings
from app.models.responses import APIResponse, ComponentStatus, HealthData

router = APIRouter()
_start_time = time.time()


@router.get("/health", response_model=APIResponse)
async def health_check(request: Request):
    settings = get_settings()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Check vector store
    vs_status = "unknown"
    vs_latency = None
    try:
        from app.dependencies import get_vector_store

        vs = get_vector_store()
        t0 = time.time()
        healthy = vs.health_check()
        vs_latency = int((time.time() - t0) * 1000)
        vs_status = "healthy" if healthy else "unhealthy"
    except Exception:
        vs_status = "unhealthy"

    # Check embedder
    emb_status = "unknown"
    emb_model = settings.embedding_model
    try:
        from app.pipeline.embedder import get_embedder

        embedder = get_embedder()
        emb_status = "loaded" if embedder is not None else "not_loaded"
    except Exception:
        emb_status = "not_loaded"

    components = {
        "vector_store": ComponentStatus(
            type=settings.vector_store,
            status=vs_status,
            latency_ms=vs_latency,
        ),
        "llm_provider": ComponentStatus(
            type=settings.llm_provider,
            status="configured" if settings.groq_api_key else "no_api_key",
            model=settings.groq_model,
        ),
        "embedding_model": ComponentStatus(
            type="sentence-transformers",
            model=emb_model,
            status=emb_status,
            dimension=384,
        ),
    }

    data = HealthData(
        service=settings.app_name,
        version=settings.app_version,
        status="healthy",
        components=components,
        uptime_seconds=round(time.time() - _start_time, 1),
    )

    return APIResponse(status="success", data=data, request_id=request_id)
