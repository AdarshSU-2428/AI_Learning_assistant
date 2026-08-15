import uuid
import chromadb
from langchain_core.documents import Document

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
        self.collection_name = collection_name or COLLECTION_NAME

        try:
            self.logger.info("Initializing ChromaDB...")

            self.client = chromadb.PersistentClient(path=self.persist_directory)

            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            self.get_all_subjects(force_refresh=True)

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

            clean_metadatas = []
            for doc in documents:
                meta = doc.metadata or {}
                clean_meta = {}
                for k, v in meta.items():
                    if v is None:
                        clean_meta[k] = ""
                    elif isinstance(v, (str, int, float, bool)):
                        clean_meta[k] = v
                    else:
                        clean_meta[k] = str(v)
                clean_metadatas.append(clean_meta)

            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings.tolist(),
                metadatas=clean_metadatas
            )

            VectorStore._cached_subjects = None
            self.logger.info(f"Successfully stored {len(documents)} documents.")

            return len(documents)

        except Exception as e:
            self.logger.error(f"Vector storage failed: {e}")
            raise

    def similarity_search(self, query_embedding, top_k, where=None):
        self.logger.info(f"Searching top {top_k} similar documents...")

        try:
            if top_k <= 0:
                raise ValueError("top_k must be greater than 0.")

            if query_embedding is None:
                raise ValueError("Query embedding cannot be None.")

            query_kwargs = {
                "query_embeddings": [query_embedding.tolist()],
                "n_results": top_k
            }
            
            if where:
                query_kwargs["where"] = where

            results = self.collection.query(**query_kwargs)

            retrieved_documents = []

            for text, metadata in zip(
                results["documents"][0],
                results["metadatas"][0]
            ):
                retrieved_documents.append(
                    Document(
                        page_content=text,
                        metadata=metadata
                    )
                )

            if not retrieved_documents:
                self.logger.warning("No similar documents found.")
            else:
                self.logger.info(f"Retrieved {len(retrieved_documents)} similar documents.")

            return retrieved_documents

        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            raise
    
    _cached_subjects = None

    def get_all_subjects(self, force_refresh=False):
        if VectorStore._cached_subjects is not None and not force_refresh:
            return VectorStore._cached_subjects

        try:
            subjects = set()
            from config.settings import DOCUMENTS_PATH, LAB_DATA_PATH, QUIZ_DATA_PATH
            check_dirs = [
                DOCUMENTS_PATH / "Notes",
                LAB_DATA_PATH / "Lab Assignments",
                LAB_DATA_PATH / "Lab Manuals",
                QUIZ_DATA_PATH
            ]
            for p in check_dirs:
                if p.exists():
                    for entry in p.iterdir():
                        if entry.is_dir() and entry.name.lower() not in ("__pycache__", ".git", ".idea"):
                            subjects.add(entry.name)

            if not subjects:
                results = self.collection.get(include=["metadatas"])
                metadatas = results.get("metadatas", [])
                for m in metadatas:
                    if isinstance(m, dict) and "subject" in m and m["subject"]:
                        subjects.add(m["subject"])

            VectorStore._cached_subjects = sorted(list(subjects))
            return VectorStore._cached_subjects

        except Exception as e:
            self.logger.error(f"Failed to retrieve subjects: {e}")
            return []
