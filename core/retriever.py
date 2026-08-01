from utils.logger import get_logger
from config.settings import RETRIEVAL_TOP_K
from core.embedding_model import EmbeddingModel
from core.vector_store import VectorStore


class RetrievalConfig:
    def __init__(
        self,
        top_k=RETRIEVAL_TOP_K,
        subject=None,
        content_type=None,
        source_type=None
    ):
        self.top_k = top_k
        self.subject = subject
        self.content_type = content_type
        self.source_type = source_type

    def get_where_filter(self):
        filters = []
        if self.subject:
            filters.append(
                {
                    "subject": self.subject
                }
            )
        if self.content_type:
            filters.append(
                {
                    "content_type": self.content_type
                }
            )
        if self.source_type:
            filters.append(
                {
                    "source_type": self.source_type
                }
            )

        if not filters:
            return None

        if len(filters) == 1:
            return filters[0]

        return {
            "$and": filters
        }


class Retriever:
    def __init__(self):
        self.logger = get_logger(__name__)

        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()

    def retrieve(self, query, config=None, top_k=None):
        self.logger.info("Starting document retrieval...")

        try:
            if isinstance(config, RetrievalConfig):
                effective_top_k = config.top_k
                where_filter = config.get_where_filter()
            else:
                effective_top_k = top_k if top_k is not None else RETRIEVAL_TOP_K
                where_filter = None

            query_embedding = self.embedding_model.generate_query_embedding(query)

            search_kwargs = {
                "query_embedding": query_embedding,
                "top_k": effective_top_k,
            }
            if where_filter is not None:
                search_kwargs["where"] = where_filter

            retrieved_documents = self.vector_store.similarity_search(**search_kwargs)

            self.logger.info(
                f"Retrieved {len(retrieved_documents)} documents successfully (top_k={effective_top_k}, filter={where_filter})."
            )

            return retrieved_documents

        except Exception as e:
            self.logger.error(f"Document retrieval failed: {e}")
            raise