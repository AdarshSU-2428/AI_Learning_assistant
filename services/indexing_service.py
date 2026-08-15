import os
import uuid

from utils.logger import get_logger

from core.loaders.pdf_loader import PDFLoader
from core.loaders.docx_loader import DOCXLoader
from core.loaders.ppt_loader import PPTLoader

from core.preprocesser import Preprocessor
from core.chunker import Chunker
from core.embedding_model import EmbeddingModel
from core.vector_store import VectorStore
from core.index_manager import IndexManager


import json

from config.settings import (
    QUIZ_COLLECTION_NAME, 
    QUIZ_DATA_PATH, 
    COLLECTION_NAME,
    LAB_COLLECTION_NAME,
    LAB_DATA_PATH
)

class IndexingService:
    def __init__(self):
        self.logger = get_logger(__name__)

        self.loaders = {
            ".pdf": PDFLoader(),
            ".docx": DOCXLoader(),
            ".pptx": PPTLoader(),
        }

        self.preprocesser = Preprocessor()
        self.chunker = Chunker()
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(collection_name=COLLECTION_NAME)
        self.quiz_vector_store = VectorStore(collection_name=QUIZ_COLLECTION_NAME)
        self.lab_vector_store = VectorStore(collection_name=LAB_COLLECTION_NAME)
        self.index_manager = IndexManager()

    def _index_document(self, file_path):
        self.logger.info(f"Indexing file: {file_path}")

        try:
            extension = os.path.splitext(file_path)[1].lower()

            loader = self.loaders.get(extension)

            if loader is None:
                raise ValueError(f"Unsupported file type: {extension}")

            units = loader.load(file_path)

            document_id = str(uuid.uuid4())

            documents = []
            next_chunk_id = 0

            for unit in units:
                text = unit["text"]
                metadata = unit["metadata"]

                preprocessed_text, preprocessed_metadata = (
                    self.preprocesser.preprocess(text, metadata)
                )

                if not preprocessed_text or not preprocessed_text.strip():
                    continue

                chunks = self.chunker.chunk_text(
                    preprocessed_text,
                    preprocessed_metadata,
                    start_chunk_id=next_chunk_id,
                )

                documents.extend(chunks)
                next_chunk_id += len(chunks)

            embeddings, valid_docs = self.embedding_model.generate_embeddings(
                documents
            )

            is_quiz = "quiz" in file_path.lower() or "\\quiz\\" in file_path.lower() or "/quiz/" in file_path.lower()
            is_lab = "lab" in file_path.lower() or "\\lab\\" in file_path.lower() or "/lab/" in file_path.lower()
            
            if is_quiz:
                stored_count = self.quiz_vector_store.store(valid_docs, embeddings)
                self.index_manager.register_quiz_document(
                    file_path=file_path, 
                    document_id=document_id, 
                    chunks=stored_count
                )

            elif is_lab:
                stored_count = self.lab_vector_store.store(valid_docs, embeddings)
                self.index_manager.register_lab_document(
                    file_path=file_path,
                    document_id=document_id,
                    chunks=stored_count
                )
                
            else:
                stored_count = self.vector_store.store(valid_docs, embeddings)
                self.index_manager.register_document(
                    file_path=file_path, 
                    document_id=document_id, 
                    chunks=stored_count
                )

            self.logger.info(f"Successfully indexed {file_path}")

            return stored_count

        except Exception as e:
            self.logger.error(f"Failed to index '{file_path}': {e}")
            raise

    def index_directory(self, folder_path):
        self.logger.info(f"Starting indexing for the directory: {folder_path}")

        try:
            if not os.path.isdir(folder_path):
                raise ValueError(f"Directory not found: {folder_path}")

            total_files = 0
            total_chunks = 0
            failed_files = []

            for root, _, files in os.walk(folder_path):
                for filename in files:
                    file_path = os.path.join(root, filename)

                    extension = os.path.splitext(filename)[1].lower()

                    if extension not in self.loaders:
                        self.logger.warning(f"Skipping unsupported file: {file_path}")
                        continue

                    is_quiz = "quiz" in file_path.lower() or "\\quiz\\" in file_path.lower() or "/quiz/" in file_path.lower()
                    is_lab = "lab" in file_path.lower() or "\\lab\\" in file_path.lower() or "/lab/" in file_path.lower()

                    if is_quiz:
                        is_already_indexed = self.index_manager.is_quiz_indexed(file_path)
                    elif is_lab:
                        is_already_indexed = self.index_manager.is_lab_indexed(file_path)
                    else:
                        is_already_indexed = self.index_manager.is_document_indexed(file_path)

                    if is_already_indexed:
                        self.logger.info(f"Skipping already indexed file: {file_path}")
                        continue

                    try:
                        stored = self._index_document(file_path)

                        total_files += 1
                        total_chunks += stored

                    except Exception as e:
                        self.logger.error(f"Skipping '{filename}' due to indexing error: {e}")

                        failed_files.append(
                            {
                                "file": filename, 
                                "error": str(e)
                            }
                        )

            self.logger.info(f"Directory indexing completed successfully.")

            return {
                "status": "success",
                "indexed_files": total_files,
                "failed_files": failed_files,
                "chunks_stored": total_chunks,
            }

        except Exception as e:
            self.logger.exception(f"Directory indexing failed: {e}")
            raise

    def index_quiz_file(self, file_path, subject=None):
        self.logger.info(f"Indexing quiz file: {file_path}")
        try:
            filename = os.path.basename(file_path)
            inferred_subject = subject or os.path.splitext(filename)[0].replace("_", " ")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            raw_questions = json.loads(content)
            if isinstance(raw_questions, dict) and "questions" in raw_questions:
                raw_questions = raw_questions["questions"]
            elif not isinstance(raw_questions, list):
                raw_questions = [raw_questions]

            documents = []
            for item in raw_questions:
                if not isinstance(item, dict) or not item.get("question"):
                    continue

                q_text = item["question"]
                options = item.get("options", [])
                correct_ans = str(item.get("correct_answer", "")).strip().upper()
                difficulty = item.get("difficulty", "Standard")
                hint = item.get("hint", "")
                explanation = item.get("explanation", "")

                metadata = {
                    "subject": inferred_subject,
                    "difficulty": difficulty,
                    "correct_answer": correct_ans,
                    "options": json.dumps(options),
                    "hint": hint,
                    "explanation": explanation,
                    "source_type": "quiz_bank",
                    "file_name": filename
                }

                documents.append(
                    Document(
                        page_content=f"{inferred_subject} {difficulty} {q_text}",
                        metadata=metadata
                    )
                )

            if not documents:
                return 0

            embeddings, valid_docs = self.embedding_model.generate_embeddings(documents)
            stored_count = self.quiz_vector_store.store(valid_docs, embeddings)
            self.logger.info(f"Stored {stored_count} quiz questions for '{inferred_subject}' in quiz_bank collection.")
            return stored_count

        except Exception as e:
            self.logger.error(f"Failed to index quiz file '{file_path}': {e}")
            raise

    def index_quiz_directory(self, folder_path=None):
        target_dir = folder_path or QUIZ_DATA_PATH
        self.logger.info(f"Indexing quiz directory: {target_dir}")

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            return {"status": "success", "indexed_files": 0, "questions_stored": 0}

        total_files = 0
        total_questions = 0
        failed = []

        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith((".json", ".quiz.json")):
                    file_path = os.path.join(root, file)
                    try:
                        stored = self.index_quiz_file(file_path)
                        total_files += 1
                        total_questions += stored
                    except Exception as err:
                        failed.append({"file": file, "error": str(err)})

        return {
            "status": "success",
            "indexed_files": total_files,
            "questions_stored": total_questions,
            "failed_files": failed
        }
        
    def index_lab_file(self, file_path):
        self.logger.info(f"Indexing lab file: {file_path}")
        return self._index_document(file_path)

    def index_lab_directory(self, folder_path=None):
        target_dir = folder_path or LAB_DATA_PATH
        self.logger.info(f"Indexing lab directory: {target_dir}")

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            return {"status": "success", "indexed_files": 0, "chunks_stored": 0}

        return self.index_directory(target_dir)
