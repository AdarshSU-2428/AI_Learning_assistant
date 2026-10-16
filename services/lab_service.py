from core.retriever import Retriever, RetrievalConfig
from core.reranker import Reranker
from core.relevance_gate import RelevanceGate
from core.prompt_builder import PromptBuilder
from core.llm_client import LLMClient
from core.safety_manager import SafetyManager
from utils.logger import get_logger
from config.prompts import LAB_SYSTEM_PROMPT, LAB_USER_PROMPT
from config.settings import (
    RETRIEVAL_TOP_K, 
    LAB_COLLECTION_NAME, 
    COLLECTION_NAME,
    LAB_LLM_MODEL
)


class LabService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.lab_retriever = Retriever(collection_name=LAB_COLLECTION_NAME)
        self.notes_retriever = Retriever(collection_name=COLLECTION_NAME)
        self.reranker = Reranker()
        self.relevance_gate = RelevanceGate()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient(model=LAB_LLM_MODEL)
        self.safety_manager = SafetyManager()

    def chat(self, question, subject=None):
        self.logger.info(f"Processing lab mode query for question: '{question}' (subject: {subject})")

        try:
            if not question or not str(question).strip():
                raise ValueError("Question cannot be empty.")

            sanitized_question = self.safety_manager.sanitize_input(question)

            if not sanitized_question:
                raise ValueError("Question was empty after sanitization.")

            self.logger.info(f"Sanitized Lab Question: {sanitized_question}")

            lab_config = RetrievalConfig(top_k=RETRIEVAL_TOP_K, subject=subject, content_type=None)
            retrieved_docs = self.lab_retriever.retrieve(sanitized_question, config=lab_config) or []

            if not retrieved_docs:
                self.logger.info("No documents in lab_manual collection, safely checking course notes.")
                try:
                    notes_config = RetrievalConfig(top_k=RETRIEVAL_TOP_K, subject=subject, content_type=None)
                    retrieved_docs = self.notes_retriever.retrieve(sanitized_question, config=notes_config) or []
                except Exception as ne:
                    self.logger.warning(f"Fallback notes retrieval warning: {ne}")

            if not retrieved_docs:
                self.logger.warning("No lab manuals or course notes were retrieved.")
                return {
                    "query": sanitized_question,
                    "answer": "I'm sorry, but this practical experiment or topic does not appear to be covered in the curriculum syllabus for this subject. Please verify your selected subject in the sidebar or rephrase your question.",
                    "sources": [],
                    "is_relevant": False
                }

            scored_docs = self.reranker.score_documents(sanitized_question, retrieved_docs, top_k=20)

            accepted_docs, is_relevant = self.relevance_gate.evaluate_relevance(scored_docs)

            if not is_relevant or not accepted_docs:
                self.logger.warning("Lab query rejected by RelevanceGate (out-of-syllabus or low confidence).")
                return {
                    "query": sanitized_question,
                    "answer": "I'm sorry, but this practical experiment or topic does not appear to be covered in the curriculum syllabus for this subject. Please verify your selected subject in the sidebar or rephrase your question.",
                    "sources": [],
                    "is_relevant": False
                }

            messages = self.prompt_builder.build_messages(
                LAB_SYSTEM_PROMPT, LAB_USER_PROMPT, sanitized_question, accepted_docs, subject=subject
            )

            self.logger.info("Lab prompt messages built successfully.")

            raw_answer = self.llm.generate_response(messages)

            if not raw_answer:
                raise RuntimeError("LLM failed to generate a response for lab query.")

            clean_answer = self.safety_manager.sanitize_output(raw_answer)

            self.logger.info("Successfully generated and sanitized lab response.")

            return {
                "query": sanitized_question,
                "answer": clean_answer,
                "sources": accepted_docs,
                "is_relevant": True
            }

        except Exception as e:
            self.logger.exception(f"Error while processing lab query: {e}")
            raise

    def process_query(self, question, subject=None):
        return self.chat(question, subject=subject)
