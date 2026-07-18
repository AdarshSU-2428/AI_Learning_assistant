import unittest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from core.reranker import Reranker
from config.settings import RERANK_TOP_K

class TestReranker(unittest.TestCase):
    @patch("core.reranker.CrossEncoder")
    def setUp(self, mock_cross_encoder):
        self.mock_model_instance = MagicMock()
        mock_cross_encoder.return_value = self.mock_model_instance
        self.reranker = Reranker()

    def test_init_success(self):
        self.assertEqual(self.reranker.model_name, "cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.assertIsNotNone(self.reranker.model)

    def test_rerank_empty_documents(self):
        result = self.reranker.rerank("query", [])
        self.assertEqual(result, [])
        self.mock_model_instance.predict.assert_not_called()

    def test_rerank_invalid_top_k_raises(self):
        docs = [Document(page_content="doc1")]
        with self.assertRaises(ValueError):
            self.reranker.rerank("query", docs, top_k=0)
        with self.assertRaises(ValueError):
            self.reranker.rerank("query", docs, top_k=-1)

    def test_rerank_success(self):
        docs = [
            Document(page_content="doc1 content", metadata={"file_name": "doc1.pdf"}),
            Document(page_content="doc2 content", metadata={"file_path": "path\\to\\doc2.docx"}),
            Document(page_content="doc3 content", metadata={"source": "http://example.com/doc3.pptx"}),
            Document(page_content="doc4 content", metadata={"id": 42}),
            Document(page_content="doc5 content", metadata={}),
        ]
        # Mock scores returned by cross-encoder model.predict
        # doc1: 0.1, doc2: 0.9, doc3: 0.5, doc4: 0.7, doc5: 0.2
        mock_scores = [0.1, 0.9, 0.5, 0.7, 0.2]
        self.mock_model_instance.predict.return_value = mock_scores

        # Rerank and return top 3 documents
        result = self.reranker.rerank("test query", docs, top_k=3)

        # Expected sorted order by score descending:
        # doc2 (0.9), doc4 (0.7), doc3 (0.5), doc5 (0.2), doc1 (0.1)
        # top 3 should be: doc2, doc4, doc3
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].page_content, "doc2 content")
        self.assertEqual(result[0].metadata["file_path"], "path\\to\\doc2.docx")
        self.assertEqual(result[1].page_content, "doc4 content")
        self.assertEqual(result[2].page_content, "doc3 content")

        # Verify correct pairs passed to predict
        expected_pairs = [
            ["test query", "doc1 content"],
            ["test query", "doc2 content"],
            ["test query", "doc3 content"],
            ["test query", "doc4 content"],
            ["test query", "doc5 content"],
        ]
        self.mock_model_instance.predict.assert_called_once_with(expected_pairs)

    def test_rerank_failure_propagates(self):
        docs = [Document(page_content="doc1 content")]
        self.mock_model_instance.predict.side_effect = RuntimeError("Prediction error")

        with self.assertRaises(RuntimeError):
            self.reranker.rerank("query", docs)

if __name__ == "__main__":
    unittest.main()
