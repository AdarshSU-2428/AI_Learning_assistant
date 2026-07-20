import re

from core.retriever import Retriever
from core.reranker import Reranker
from core.prompt_builder import PromptBuilder
from core.llm_client import LLMClient
from core.response_sanitizer import ResponseSanitizer

from utils.logger import get_logger

from config.prompts import SYSTEM_PROMPT, USER_PROMPT

class ChatService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.retriever = Retriever()
        self.reranker = Reranker()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient()

    def _sanitize_question(self, question: str) -> str:
        self.logger.info("Sanitizing question for potential prompt injection...")
        
        injection_patterns = [
            r"(?i)\bignore\s+previous\s+instructions\b",
            r"(?i)\breveal\s+(?:your\s+)?system\s+prompt\b",
            r"(?i)\breveal\s+(?:your\s+)?prompt\b",
            r"(?i)\bdecode\s+(?:the\s+)?system\s+prompt\b",
            r"(?i)\bignore\s+above\s+instructions\b"
        ]
        
        sanitized = question
        for pattern in injection_patterns:
            sanitized = re.sub(pattern, "", sanitized)
            
  
        sanitized = sanitized.lstrip(" .!?,-_")
    
        return sanitized.rstrip(" .,-_")

    def chat(self, question):
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        question = self._sanitize_question(question)
        if not question:
            raise ValueError("Question was empty after sanitization.")

        self.logger.info(f"User Question: {question}")

        try:
            retrieved_docs = self.retriever.retrieve(question)

            if not retrieved_docs:
                self.logger.warning("No relevant documents were retrieved.")
                return {
                    "query": question,
                    "answer": "I don't have enough information to answer this question accurately.",
                    "sources": []
                }

            self.logger.info(f"Retrieved {len(retrieved_docs)} documents.")

            reranked_docs = self.reranker.rerank(question, retrieved_docs)
            self.logger.info(f"Reranked to {len(reranked_docs)} documents.")

            if not reranked_docs:
                self.logger.warning(
                    "No documents passed the reranker confidence threshold."
                )
                return {
                    "query": question,
                    "answer": "I don't have enough information to answer this question accurately.",
                    "sources": []
                }

            messages = self.prompt_builder.build_messages(SYSTEM_PROMPT, USER_PROMPT, question, reranked_docs)
            self.logger.info("Messages built successfully.")

            answer = self.llm.generate_response(messages)
            if not answer:
                raise RuntimeError("LLM failed to generate a response.")

            answer = ResponseSanitizer.clean(answer)

            self.logger.info("Successfully generated LLM response.")

            return {
                "query": question,
                "answer": answer,
                "sources": reranked_docs
            }


        except Exception as e:
            self.logger.exception(f"Error while processing query: {e}")
            raise