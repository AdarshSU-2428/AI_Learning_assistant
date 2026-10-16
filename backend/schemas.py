from typing import Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    subject: str | None = None


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: list[Any] = []
    is_relevant: bool = True


class QuizRequest(BaseModel):
    topic: str
    subject: str | None = None
    num_questions: int | None = None
    difficulty: str | None = None


class QuizResponse(BaseModel):
    topic: str
    difficulty: str | None = None
    questions: list[Any] = []
    sources: list[Any] = []
    is_relevant: bool = True
    message: str = ""


class QuizSubmissionRequest(BaseModel):
    quiz_questions: list[dict[str, Any]]
    user_answers: dict[str | int, str]


class QuizSubmissionResponse(BaseModel):
    score: int
    total: int
    percentage: float
    details: list[dict[str, Any]] = []


class ExamGenerateRequest(BaseModel):
    subject: str
    num_questions: int | None = None


class ExamGenerateResponse(BaseModel):
    subject: str
    total_marks: int = 0
    questions: list[dict[str, Any]] = []
    sources: list[Any] = []
    is_relevant: bool = True
    message: str = ""


