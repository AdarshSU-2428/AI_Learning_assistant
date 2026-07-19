from core.retriever import Retriever
from core.reranker import Reranker
from core.prompt_builder import PromptBuilder
from core.llm_client import LLMClient

from utils.logger import get_logger

from config.prompts import SYSTEM_PROMPT

class ChatService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.retriever = Retriever()
        self.reranker = Reranker()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient()

    def chat(self, question):
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        question = question.strip()
        self.logger.info(f"User Question: {question}")

        try:
            retrieved_docs = self.retriever.retrieve(question)

            if not retrieved_docs:
                self.logger.warning("No relevant documents were retrieved.")
                return {
                    "query": question,
                    "answer": "I couldn't find any relevant information in the indexed documents.",
                    "documents": []
                }

            self.logger.info(f"Retrieved {len(retrieved_docs)} documents.")

            reranked_docs = self.reranker.rerank(question, retrieved_docs)
            self.logger.info(f"Reranked to {len(reranked_docs)} documents.")

            prompt = self.prompt_builder.build_prompt(SYSTEM_PROMPT, question, reranked_docs)
            self.logger.info("Prompt built successfully.")

            answer = self.llm.generate_response(prompt)
            if not answer:
                raise RuntimeError("LLM failed to generate a response.")

            self.logger.info("Successfully generated LLM response.")

            return {
                "query": question,
                "answer": answer,
                "sources": reranked_docs
            }


        except Exception as e:
            self.logger.exception(f"Error while processing query: {e}")
            raise