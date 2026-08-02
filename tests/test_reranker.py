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

    def test_score_documents_empty_documents(self):
        result = self.reranker.score_documents("query", [])
        self.assertEqual(result, [])
        self.mock_model_instance.predict.assert_not_called()

    def test_score_documents_invalid_top_k_raises(self):
        docs = [Document(page_content="doc1")]
        with self.assertRaises(ValueError):
            self.reranker.score_documents("query", docs, top_k=0)
        with self.assertRaises(ValueError):
            self.reranker.score_documents("query", docs, top_k=-1)

    def test_score_documents_success(self):
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

        # Score documents and return top 3 scored pairs
        results = self.reranker.score_documents("test query", docs, top_k=3)

        # Expected sorted order by score descending:
        # doc2 (0.9), doc4 (0.7), doc3 (0.5)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][0].page_content, "doc2 content")
        self.assertAlmostEqual(results[0][1], 0.9)
        self.assertEqual(results[1][0].page_content, "doc4 content")
        self.assertAlmostEqual(results[1][1], 0.7)
        self.assertEqual(results[2][0].page_content, "doc3 content")
        self.assertAlmostEqual(results[2][1], 0.5)

    def test_rerank_returns_ranked_documents(self):
        docs = [
            Document(page_content="good doc", metadata={"source": "good.pdf"}),
            Document(page_content="borderline doc", metadata={"source": "borderline.pdf"}),
            Document(page_content="bad doc", metadata={"source": "bad.pdf"}),
        ]
        mock_scores = [0.8, 0.35, 0.15]
        self.mock_model_instance.predict.return_value = mock_scores

        result = self.reranker.rerank("query", docs, top_k=3)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].page_content, "good doc")
        self.assertEqual(result[1].page_content, "borderline doc")
        self.assertEqual(result[2].page_content, "bad doc")

    def test_rerank_failure_propagates(self):
        docs = [Document(page_content="doc1 content")]
        self.mock_model_instance.predict.side_effect = RuntimeError("Prediction error")

        with self.assertRaises(RuntimeError):
            self.reranker.rerank("query", docs)


if __name__ == "__main__":
    unittest.main()
