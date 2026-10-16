import logging
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

from backend.dependencies import app_service
from backend.schemas import (
    ChatRequest,
    ChatResponse,
    QuizRequest,
    QuizResponse,
    QuizSubmissionRequest,
    QuizSubmissionResponse,
    ExamGenerateRequest,
    ExamGenerateResponse
)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask a question to the AI Learning Assistant",
)
def chat(request: ChatRequest):
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

    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Backend processing error: {str(exc)}",
        )


@router.post(
    "/quiz/generate",
    response_model=QuizResponse,
    summary="Generate an interactive multiple-choice quiz",
)
def generate_quiz(request: QuizRequest):
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

    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Backend processing error: {str(exc)}",
        )


@router.post(
    "/quiz/evaluate",
    response_model=QuizSubmissionResponse,
    summary="Evaluate student quiz answers and compute score",
)
def evaluate_quiz(request: QuizSubmissionRequest):
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

    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Backend processing error: {str(exc)}",
        )


@router.post(
    "/lab/chat",
    response_model=ChatResponse,
    summary="Ask a practical experiment or coding lab question",
)
def lab_chat(request: ChatRequest):
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

    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Backend processing error: {str(exc)}",
        )

@router.post(
    "/exam/generate",
    response_model=ExamGenerateResponse,
    summary="Generate a written university examination paper"
)
def generate_exam(request: ExamGenerateRequest):
    try:
        response = app_service.generate_exam(
            subject=request.subject,
            num_questions=request.num_questions
        )
        return response

    except ValueError as exc:
        logger.warning(f"ValueError in generate_exam route: {exc}")
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        logger.error(f"Error in generate_exam route: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(exc)}"
        )