from sentence_transformers import CrossEncoder
from utils.logger import get_logger

from config.settings import (RERANK_TOP_K, RERANKER_MODEL, RERANK_SCORE_THRESHOLD)


class Reranker:
    def __init__(self, model_name=RERANKER_MODEL):
        self.logger = get_logger(__name__)

        self.model_name = model_name

        try:
            self.model = CrossEncoder(self.model_name)

            self.logger.info(f"Loaded reranker model: {self.model_name}")

        except Exception as e:
            self.logger.error(f"Failed to load reranker model: {e}")
            raise

    def rerank(self, query, documents, top_k=RERANK_TOP_K):
        self.logger.info("Starting reranking...")

        try:
            if not documents:
                self.logger.warning("No documents to rerank.")
                return []

            if top_k <= 0:
                raise ValueError("top_k must be greater than 0.")

            pairs = [[query, document.page_content] for document in documents]

            scores = self.model.predict(pairs)

            scored_documents = list(zip(documents, scores))

            scored_documents.sort(key=lambda item: item[1], reverse=True)

            for document, score in scored_documents:
                metadata = document.metadata or {}

                source = (
                    metadata.get("file_name") or
                    (metadata.get("file_path") or metadata.get("source") or "").replace("\\", "/").split("/")[-1] or
                    (str(metadata.get("id")) if "id" in metadata else None) or
                    "Unknown"
                )

                self.logger.info(f"[Reranker] {source} | Score: {score:.4f}")

            reranked_documents = [
                document
                for document, score in scored_documents
                if score >= RERANK_SCORE_THRESHOLD
            ][:top_k]

            if not reranked_documents:
                self.logger.info(
                    "No documents passed the reranker confidence threshold."
                )
                return []

            self.logger.info(f"Successfully reranked {len(reranked_documents)} documents.")

            return reranked_documents

        except Exception as e:
            self.logger.error(f"Reranking failed: {e}")
            raise