import uuid
import chromadb
from langchain_core.documents import Document

from utils.logger import get_logger
from config.settings import (
    VECTOR_DB_PATH, 
    COLLECTION_NAME,
    DOCUMENTS_PATH, 
    LAB_DATA_PATH, 
    QUIZ_DATA_PATH, 
    EXAM_DATA_PATH
)

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

    def reset_collection(self):
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            VectorStore._cached_subjects = None
            self.logger.info(f"Reset collection '{self.collection_name}' successfully.")
        except Exception as e:
            self.logger.error(f"Failed to reset collection: {e}")

    def delete_by_file(self, file_name):
        try:
            self.collection.delete(where={"file_name": str(file_name)})
            VectorStore._cached_subjects = None
            self.logger.info(f"Cleared existing chunks for '{file_name}' from collection '{self.collection_name}'.")
        except Exception as e:
            self.logger.warning(f"Could not clear existing chunks for '{file_name}': {e}")

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

            # Attempt native ChromaDB semantic vector search first
            if query_embedding is not None:
                try:
                    q_kwargs = {
                        "query_embeddings": [query_embedding.tolist()],
                        "n_results": max(top_k * 2, 20)
                    }
                    if where and isinstance(where, dict):
                        def _format_cond(k, v):
                            if isinstance(v, dict):
                                return {k: v}
                            return {k: {"$eq": v}}

                        if "$and" in where and isinstance(where["$and"], list):
                            conds = []
                            for item in where["$and"]:
                                if isinstance(item, dict):
                                    for k, v in item.items():
                                        conds.append(_format_cond(k, v))
                            q_kwargs["where"] = {"$and": conds} if len(conds) > 1 else (conds[0] if conds else where)
                        elif len(where) > 1:
                            conds = [_format_cond(k, v) for k, v in where.items()]
                            q_kwargs["where"] = {"$and": conds}
                        else:
                            q_kwargs["where"] = where

                    res = self.collection.query(**q_kwargs)
                    if res and res.get("documents") and res["documents"][0]:
                        docs = res["documents"][0]
                        metas = res.get("metadatas", [[]])[0]
                        results = [
                            Document(page_content=txt, metadata=m or {})
                            for txt, m in zip(docs, metas)
                        ]
                        self.logger.info(f"ChromaDB semantic query retrieved {len(results)} relevant documents.")
                        return results
                except Exception as query_err:
                    self.logger.warning(f"ChromaDB query fallback triggered: {query_err}")

            # Extract target subjects for Python-side fallback filtering
            target_subjects = None
            if where and isinstance(where, dict):
                conds = where.get("$and", [where])
                for c in conds:
                    if isinstance(c, dict) and "subject" in c:
                        s_val = c["subject"]
                        if isinstance(s_val, dict) and "$in" in s_val:
                            target_subjects = [str(x).lower() for x in s_val["$in"]]
                        elif isinstance(s_val, str):
                            target_subjects = [s_val.lower()]

            # Safely fetch documents & metadatas via SQLite fallback
            raw = self.collection.get(include=["documents", "metadatas"])
            
            if not raw or not raw.get("documents"):
                self.logger.warning("No documents found in collection.")
                return []

            docs = raw["documents"]
            metas = raw.get("metadatas") or []

            retrieved_documents = []
            for idx in range(len(docs)):
                text = docs[idx]
                meta = metas[idx] if idx < len(metas) else {}

                if target_subjects and meta:
                    doc_sub = str(meta.get("subject", "")).lower()
                    if doc_sub not in target_subjects:
                        continue

                retrieved_documents.append(
                    Document(page_content=text, metadata=meta)
                )

            self.logger.info(f"Retrieved {len(retrieved_documents)} candidate documents successfully.")
            return retrieved_documents[:max(top_k * 2, 20)]

        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            raise
    
    _cached_subjects = None

    def get_all_subjects(self, force_refresh=False):
        if VectorStore._cached_subjects is not None and not force_refresh:
            return VectorStore._cached_subjects

        try:
            subjects = set()
           
            check_dirs = [
                DOCUMENTS_PATH / "Notes",
                LAB_DATA_PATH / "Lab Assignments",
                LAB_DATA_PATH / "Lab Manuals",
                QUIZ_DATA_PATH,
                EXAM_DATA_PATH
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
