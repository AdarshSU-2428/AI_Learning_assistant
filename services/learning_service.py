from core.retriever import Retriever, RetrievalConfig
from core.reranker import Reranker
from core.relevance_gate import RelevanceGate
from core.prompt_builder import PromptBuilder
from core.llm_client import LLMClient
from core.safety_manager import SafetyManager
from utils.logger import get_logger
from config.prompts import LEARNING_SYSTEM_PROMPT, LEARNING_USER_PROMPT
from config.settings import RETRIEVAL_TOP_K


class LearningService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.retriever = Retriever()
        self.reranker = Reranker()
        self.relevance_gate = RelevanceGate()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient()
        self.safety_manager = SafetyManager()

    def chat(self, question, subject=None):
        self.logger.info(f"Processing learning mode query for question: '{question}' (subject: {subject})")

        try:
            if not question or not str(question).strip():
                raise ValueError("Question cannot be empty.")

            sanitized_question = self.safety_manager.sanitize_input(question)

            if not sanitized_question:
                raise ValueError("Question was empty after sanitization.")

            self.logger.info(f"User Question: {question}")

            config = RetrievalConfig(top_k=RETRIEVAL_TOP_K, subject=subject, content_type="notes")
            retrieved_docs = self.retriever.retrieve(sanitized_question, config=config)

            if not retrieved_docs:
                self.logger.warning("No relevant documents were retrieved.")
                return {
                    "query": sanitized_question,
                    "answer": "I don't have enough information to answer this question accurately based on your course notes.",
                    "sources": [],
                    "is_relevant": False
                }

            self.logger.info(f"Retrieved {len(retrieved_docs)} candidate documents.")

            scored_docs = self.reranker.score_documents(sanitized_question, retrieved_docs, top_k=20)

            accepted_docs, is_relevant = self.relevance_gate.evaluate_relevance(scored_docs)

            if not is_relevant or not accepted_docs:
                self.logger.warning("Query rejected by RelevanceGate (out-of-syllabus or low confidence).")
                return {
                    "query": sanitized_question,
                    "answer": "I'm sorry, but this question does not appear to be covered in your uploaded course materials.",
                    "sources": [],
                    "is_relevant": False
                }

            messages = self.prompt_builder.build_messages(
                LEARNING_SYSTEM_PROMPT, LEARNING_USER_PROMPT, sanitized_question, accepted_docs
            )

            self.logger.info("Messages built successfully.")

            raw_answer = self.llm.generate_response(messages)

            if not raw_answer:
                raise RuntimeError("LLM failed to generate a response.")

            clean_answer = self.safety_manager.sanitize_output(raw_answer)

            self.logger.info("Successfully generated LLM response.")

            return {
                "query": sanitized_question,
                "answer": clean_answer,
                "sources": accepted_docs,
                "is_relevant": True
            }

        except Exception as e:
            self.logger.exception(f"Error while processing query: {e}")
            raise

    def process_query(self, question, subject=None):
        return self.chat(question, subject=subject)
