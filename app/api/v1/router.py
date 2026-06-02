from fastapi import APIRouter

from app.api.v1 import health, upload, query, documents, eval

router = APIRouter(prefix="/api/v1")

router.include_router(health.router, tags=["Health"])
router.include_router(upload.router, tags=["Upload"])
router.include_router(query.router, tags=["Query"])
router.include_router(documents.router, tags=["Documents"])
router.include_router(eval.router, tags=["Evaluation"])
