import uuid
import chromadb

from utils.logger import get_logger
from config.settings import (VECTOR_DB_PATH, COLLECTION_NAME)


class VectorStore:
    def __init__(
        self, 
        persist_directory=VECTOR_DB_PATH,
        collection_name=COLLECTION_NAME
    ):
        self.logger = get_logger(__name__)

        self.persist_directory = persist_directory
        self.collection_name = collection_name

        try:
            self.logger.info("Initializing ChromaDB...")

            self.client = chromadb.PersistentClient(path=self.persist_directory)

            self.collection = self.client.get_or_create_collection(name=self.collection_name)

            self.logger.info(f"Collection '{self.collection_name}' loaded successfully.")

        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def store(self, documents, embeddings):
        self.logger.info("Starting vector storage...")

        try:
            if not documents:
                self.logger.warning("No documents provided to store.")
                return 0

            if len(documents) != len(embeddings):
                raise ValueError("Number of documents and embeddings must match.")

            ids = [str(uuid.uuid4()) for _ in documents]

            texts = [doc.page_content for doc in documents]

            metadatas = [doc.metadata for doc in documents]

            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings.tolist(),
                metadatas=metadatas
            )

            self.logger.info(f"Successfully stored {len(documents)} documents.")

            return len(documents)

        except Exception as e:
            self.logger.error(f"Vector storage failed: {e}")
            raise


