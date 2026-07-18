from utils.logger import get_logger

from config.settings import RETRIEVAL_TOP_K

from core.embedding_model import EmbeddingModel
from core.vector_store import VectorStore


class Retriever:
    def __init__(self):
        self.logger = get_logger(__name__)

        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()

    def retrieve(self, query, top_k=RETRIEVAL_TOP_K):
        self.logger.info("Starting document retrieval...")

        try:
            query_embedding = self.embedding_model.generate_query_embedding(query)

            retrieved_documents = self.vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=top_k
            )

            self.logger.info(
                f"Retrieved {len(retrieved_documents)} documents successfully."
            )

            return retrieved_documents

        except Exception as e:
            self.logger.error(f"Document retrieval failed: {e}")
            raise