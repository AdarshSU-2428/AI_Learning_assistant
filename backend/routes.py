from fastapi import APIRouter, HTTPException

from backend.dependencies import app_service
from backend.schemas import (
    ChatRequest,
    ChatResponse,
    QuizRequest,
    QuizResponse,
    QuizSubmissionRequest,
    QuizSubmissionResponse,
)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask a question to the AI Learning Assistant",
)
async def chat(request: ChatRequest):
    try:
        response = app_service.chat(
            request.query, 
            subject=request.subject
        )
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


@router.post(
    "/quiz/generate",
    response_model=QuizResponse,
    summary="Generate an interactive multiple-choice quiz",
)
async def generate_quiz(request: QuizRequest):
    try:
        response = app_service.generate_quiz(
            topic=request.topic,
            subject=request.subject,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
        )
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


@router.post(
    "/quiz/evaluate",
    response_model=QuizSubmissionResponse,
    summary="Evaluate student quiz answers and compute score",
)
async def evaluate_quiz(request: QuizSubmissionRequest):
    try:
        response = app_service.evaluate_quiz_submission(
            quiz_questions=request.quiz_questions,
            user_answers=request.user_answers,
        )
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


@router.post(
    "/lab/chat",
    response_model=ChatResponse,
    summary="Ask a practical experiment or coding lab question",
)
async def lab_chat(request: ChatRequest):
    try:
        response = app_service.lab_chat(
            request.query, 
            subject=request.subject
        )
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
