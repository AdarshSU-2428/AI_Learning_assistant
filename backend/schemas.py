from typing import Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    subject: str | None = None


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: list[Any] = []