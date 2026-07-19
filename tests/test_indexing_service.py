import unittest
from unittest.mock import patch, MagicMock, ANY
import os
from langchain_core.documents import Document
from services.indexing_service import IndexingService

class TestIndexingService(unittest.TestCase):
    @patch("services.indexing_service.PDFLoader")
    @patch("services.indexing_service.DOCXLoader")
    @patch("services.indexing_service.PPTLoader")
    @patch("services.indexing_service.Preprocessor")
    @patch("services.indexing_service.Chunker")
    @patch("services.indexing_service.EmbeddingModel")
    @patch("services.indexing_service.VectorStore")
    @patch("services.indexing_service.IndexManager")
    def setUp(
        self,
        mock_im,
        mock_vs,
        mock_em,
        mock_chunker,
        mock_preprocessor,
        mock_ppt,
        mock_docx,
        mock_pdf
    ):
        # Mock instance setups
        self.mock_im_inst = MagicMock()
        self.mock_im_inst.is_document_indexed.return_value = False
        mock_im.return_value = self.mock_im_inst

        self.mock_preprocessor_inst = MagicMock()
        mock_preprocessor.return_value = self.mock_preprocessor_inst

        self.mock_chunker_inst = MagicMock()
        mock_chunker.return_value = self.mock_chunker_inst

        self.mock_em_inst = MagicMock()
        mock_em.return_value = self.mock_em_inst

        self.mock_vs_inst = MagicMock()
        mock_vs.return_value = self.mock_vs_inst

        # Instantiate service
        self.service = IndexingService()

    def test_init_success(self):
        self.assertIn(".pdf", self.service.loaders)
        self.assertIn(".docx", self.service.loaders)
        self.assertIn(".pptx", self.service.loaders)

    @patch("services.indexing_service.os.path.splitext")
    def test_index_document_success(self, mock_splitext):
        # Setup mocks
        mock_splitext.return_value = ("dummy_file", ".pdf")
        
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = ("Extracted Text", {"source": "dummy_file.pdf"})
        self.service.loaders[".pdf"] = mock_loader_instance

        self.mock_preprocessor_inst.preprocess.return_value = ("Preprocessed Text", {"source": "dummy_file.pdf"})
        
        mock_docs = [Document(page_content="Preprocessed Text", metadata={"source": "dummy_file.pdf"})]
        self.mock_chunker_inst.chunk_text.return_value = mock_docs
        
        mock_embeddings = [[0.1, 0.2]]
        self.mock_em_inst.generate_embeddings.return_value = (mock_embeddings, mock_docs)
        
        self.mock_vs_inst.store.return_value = 1

        # Run index document
        stored_count = self.service._index_document("dummy_file.pdf")

        # Verify calls and assertions
        self.assertEqual(stored_count, 1)
        mock_loader_instance.load.assert_called_once()
        self.mock_preprocessor_inst.preprocess.assert_called_once_with("Extracted Text", {"source": "dummy_file.pdf"})
        self.mock_chunker_inst.chunk_text.assert_called_once_with("Preprocessed Text", {"source": "dummy_file.pdf"})
        self.mock_em_inst.generate_embeddings.assert_called_once_with(mock_docs)
        self.mock_vs_inst.store.assert_called_once_with(mock_docs, mock_embeddings)
        self.mock_im_inst.register_document.assert_called_once_with(
            file_path="dummy_file.pdf",
            document_id=ANY,
            chunks=1
        )

    @patch("services.indexing_service.os.path.isdir")
    @patch("services.indexing_service.os.walk")
    def test_index_directory_success(self, mock_walk, mock_isdir):
        mock_isdir.return_value = True
        mock_walk.return_value = [("dummy_folder", [], ["file1.pdf", "file2.docx", "unsupported.txt"])]

        # Mock _index_document method on the service
        self.service._index_document = MagicMock(side_effect=[10, 5])

        result = self.service.index_directory("dummy_folder")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["indexed_files"], 2)
        self.assertEqual(result["chunks_stored"], 15)
        self.assertEqual(len(result["failed_files"]), 0)

        # Confirm _index_document was called for the two supported files
        self.assertEqual(self.service._index_document.call_count, 2)

    @patch("services.indexing_service.os.path.isdir")
    @patch("services.indexing_service.os.walk")
    def test_index_directory_skips_already_indexed(self, mock_walk, mock_isdir):
        mock_isdir.return_value = True
        mock_walk.return_value = [("dummy_folder", [], ["file1.pdf"])]
        
        # Mock index_manager to say it is already indexed
        self.mock_im_inst.is_document_indexed.return_value = True

        # Mock _index_document method on the service
        self.service._index_document = MagicMock()

        result = self.service.index_directory("dummy_folder")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["indexed_files"], 0)
        self.assertEqual(result["chunks_stored"], 0)
        self.service._index_document.assert_not_called()

    @patch("services.indexing_service.os.path.isdir")
    @patch("services.indexing_service.os.walk")
    def test_index_directory_with_failures(self, mock_walk, mock_isdir):
        mock_isdir.return_value = True
        mock_walk.return_value = [("dummy_folder", [], ["file1.pdf", "file2.docx"])]

        # Mock _index_document: first succeeds, second fails
        self.service._index_document = MagicMock(side_effect=[10, Exception("Failed to load PDF")])

        result = self.service.index_directory("dummy_folder")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["indexed_files"], 1) # only 1 file indexed successfully
        self.assertEqual(result["chunks_stored"], 10)
        self.assertEqual(len(result["failed_files"]), 1)
        self.assertEqual(result["failed_files"][0]["file"], "file2.docx")
        self.assertIn("Failed to load PDF", result["failed_files"][0]["error"])

    @patch("services.indexing_service.os.path.isdir")
    def test_index_directory_not_found(self, mock_isdir):
        mock_isdir.return_value = False
        with self.assertRaises(ValueError):
            self.service.index_directory("non_existent_folder")

if __name__ == "__main__":
    unittest.main()
