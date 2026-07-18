from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document

from utils.logger import get_logger
from config.settings import EMBEDDING_MODEL


class EmbeddingModel :
    def __init__(self, model_name=EMBEDDING_MODEL) :
        self.logger = get_logger(__name__)
        self.model_name = model_name

        try :
            self.model = SentenceTransformer(self.model_name)
            self.logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
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
                    source = document.metadata.get("source", "Unknown")

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


