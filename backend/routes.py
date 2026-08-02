from fastapi import APIRouter, HTTPException

from backend.dependencies import app_service
from backend.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask a question to the AI Learning Assistant",
)
async def chat(request: ChatRequest):

    try:
        response = app_service.chat(request.query, subject=request.subject)
        return response

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )
