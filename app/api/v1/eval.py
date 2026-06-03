import uuid

from fastapi import APIRouter, Depends, Request

from app.models.requests import EvalRequest
from app.models.responses import APIResponse, EvalData
from app.services.eval_service import EvalService, get_eval_service

router = APIRouter()


@router.post("/eval", response_model=APIResponse)
async def run_evaluation(
    body: EvalRequest,
    request: Request,
    eval_service: EvalService = Depends(get_eval_service),
):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    result = await eval_service.run_eval(
        document_id=body.document_id,
        eval_dataset=[
            {"question": item.question, "ground_truth": item.ground_truth} for item in body.eval_dataset
        ],
        request_id=request_id,
    )

    data = EvalData(**result)
    return APIResponse(status="success", data=data, request_id=request_id)
