from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document

from utils.logger import get_logger
from config.settings import EMBEDDING_MODEL


class EmbeddingModel:
    _instance = None

    def __new__(cls, model_name=EMBEDDING_MODEL):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_name=EMBEDDING_MODEL):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True
        self.logger = get_logger(__name__)
        self.model_name = model_name

        try:
            self.model = SentenceTransformer(self.model_name)
            self.logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            self.logger.warning(f"Online loading failed for embedding model ({e}), attempting local cache fallback...")
            try:
                self.model = SentenceTransformer(self.model_name, local_files_only=True)
                self.logger.info(f"Loaded embedding model from local cache: {self.model_name}")
            except Exception:
                self.logger.error(f"Error loading embedding model: {e}")
                raise

    def generate_embeddings(self, documents):
        self.logger.info("Starting embedding generation...")

        try :
            if not isinstance(documents, list):
                raise TypeError("Input must be a list of Documents.") 

            valid_documents = []

            for index, document in enumerate(documents):
                if not isinstance(document, Document):
                    raise TypeError(f"Item at index {index} is not a LangChain Document.")

                if not document.page_content or not document.page_content.strip():
                    metadata = document.metadata or {}
                    
                    source = (
                        metadata.get("file_name") or
                        (metadata.get("file_path") or metadata.get("source") or "").replace("\\", "/").split("/")[-1] or
                        (str(metadata.get("id")) if "id" in metadata else None) or
                        "Unknown"
                    )

                    self.logger.warning(
                        f"Skipped empty document at index {index} "
                        f"(source: {source})."
                    )
                else:
                    valid_documents.append(document)

            if not valid_documents :
                raise ValueError("No valid documents found for embedding.")

            self.logger.info(f"Generating embeddings for {len(valid_documents)} documents...")

            texts = [doc.page_content for doc in valid_documents]

            embeddings = self.model.encode(
                texts,
                show_progress_bar=True,
                convert_to_numpy=True,
                normalize_embeddings=True
            )   

            self.logger.info(f"Successfully generated embeddings for {len(embeddings)} documents.")

            return embeddings, valid_documents

        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}")
            raise


    def generate_query_embedding(self, query):
        self.logger.info("Generating query embedding...")

        try:
            if not isinstance(query, str):
                raise TypeError("Query must be a string.")

            if not query.strip():
                raise ValueError("Query cannot be empty.")

            embedding = self.model.encode(
                query,
                convert_to_numpy=True,
                normalize_embeddings=True
            )

            self.logger.info("Query embedding generated successfully.")

            return embedding

        except Exception as e:
            self.logger.error(f"Query embedding generation failed: {e}")
            raise