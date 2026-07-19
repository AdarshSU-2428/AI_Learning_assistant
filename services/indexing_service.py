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

class IndexingService: 
    def __init__(self):
        self.logger = get_logger(__name__)

        self.loaders = {
            '.pdf': PDFLoader(),
            '.docx': DOCXLoader(),
            '.pptx': PPTLoader()
        }

        self.preprocesser = Preprocessor()
        self.chunker = Chunker()
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()
        self.index_manager = IndexManager()

    def _index_document(self, file_path):
        self.logger.info(f"Indexing file: {file_path}")

        try:
            extension = os.path.splitext(file_path)[1].lower()
        
            loader = self.loaders.get(extension)

            if loader is None:
                raise ValueError(f"Unsupported file type: {extension}")

            text, metadata = loader.load(file_path)

            document_id = str(uuid.uuid4())

            text, metadata = self.preprocesser.preprocess(text, metadata)

            documents = self.chunker.chunk_text(text, metadata)

            embeddings, valid_docs = self.embedding_model.generate_embeddings(documents)

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

                    if self.index_manager.is_document_indexed(file_path):
                        self.logger.info(f"Skipping already indexed file: {file_path}")
                        continue

                    try:
                        stored = self._index_document(file_path)

                        total_files += 1
                        total_chunks += stored

                    except Exception as e:
                        self.logger.error(f"Skipping '{filename}' due to indexing error: {e}")

                        failed_files.append({
                            "file": filename,
                            "error": str(e)
                        })

            self.logger.info(f"Directory indexing completed successfully.")

            return {
                "status": "success",
                "indexed_files": total_files,
                "failed_files": failed_files,
                "chunks_stored": total_chunks
            }

        except Exception as e:
            self.logger.error(f"Directory indexing failed: {e}")
            raise

