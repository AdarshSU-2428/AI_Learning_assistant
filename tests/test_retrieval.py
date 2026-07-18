import unittest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from core.retriever import Retriever
from config.settings import RETRIEVAL_TOP_K

class TestRetriever(unittest.TestCase):
    @patch("core.retriever.EmbeddingModel")
    @patch("core.retriever.VectorStore")
    def setUp(self, mock_vector_store_cls, mock_embedding_model_cls):
        self.mock_embedding_model = MagicMock()
        self.mock_vector_store = MagicMock()
        
        mock_embedding_model_cls.return_value = self.mock_embedding_model
        mock_vector_store_cls.return_value = self.mock_vector_store
        
        self.retriever = Retriever()

    def test_init_success(self):
        # Assert components are initialized
        self.assertIsNotNone(self.retriever.embedding_model)
        self.assertIsNotNone(self.retriever.vector_store)

    def test_retrieve_success_with_default_top_k(self):
        query = "What is deep learning?"
        mock_embedding = [0.1, 0.2, 0.3]
        mock_docs = [
            Document(page_content="Deep learning is...", metadata={"source": "dl.pdf"}),
            Document(page_content="Neural networks are...", metadata={"source": "nn.pdf"})
        ]

        self.mock_embedding_model.generate_query_embedding.return_value = mock_embedding
        self.mock_vector_store.similarity_search.return_value = mock_docs

        results = self.retriever.retrieve(query)

        # Assert correct method calls
        self.mock_embedding_model.generate_query_embedding.assert_called_once_with(query)
        self.mock_vector_store.similarity_search.assert_called_once_with(
            query_embedding=mock_embedding,
            top_k=RETRIEVAL_TOP_K
        )
        
        # Assert returns correct documents
        self.assertEqual(results, mock_docs)

    def test_retrieve_success_with_custom_top_k(self):
        query = "C programming arrays"
        custom_top_k = 3
        mock_embedding = [0.4, 0.5, 0.6]
        mock_docs = [Document(page_content="An array is...", metadata={"source": "array.pptx"})]

        self.mock_embedding_model.generate_query_embedding.return_value = mock_embedding
        self.mock_vector_store.similarity_search.return_value = mock_docs

        results = self.retriever.retrieve(query, top_k=custom_top_k)

        # Assert correct method calls with custom top_k
        self.mock_embedding_model.generate_query_embedding.assert_called_once_with(query)
        self.mock_vector_store.similarity_search.assert_called_once_with(
            query_embedding=mock_embedding,
            top_k=custom_top_k
        )
        self.assertEqual(results, mock_docs)

    def test_retrieve_embedding_failure_raises(self):
        query = "Invalid query"
        self.mock_embedding_model.generate_query_embedding.side_effect = ValueError("Invalid query type")

        with self.assertRaises(ValueError) as context:
            self.retriever.retrieve(query)

        self.assertIn("Invalid query type", str(context.exception))
        self.mock_vector_store.similarity_search.assert_not_called()

    def test_retrieve_vector_store_failure_raises(self):
        query = "Valid query"
        mock_embedding = [0.1, 0.2]
        self.mock_embedding_model.generate_query_embedding.return_value = mock_embedding
        self.mock_vector_store.similarity_search.side_effect = RuntimeError("Database connection lost")

        with self.assertRaises(RuntimeError) as context:
            self.retriever.retrieve(query)

        self.assertIn("Database connection lost", str(context.exception))
        self.mock_embedding_model.generate_query_embedding.assert_called_once_with(query)

if __name__ == "__main__":
    unittest.main()
