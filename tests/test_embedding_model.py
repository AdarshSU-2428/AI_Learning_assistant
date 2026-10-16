import unittest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from core.embedding_model import EmbeddingModel

class TestEmbeddingModel(unittest.TestCase):
    @patch("core.embedding_model.SentenceTransformer")
    def setUp(self, mock_transformer):
        EmbeddingModel._instance = None
        self.mock_model_instance = MagicMock()
        mock_transformer.return_value = self.mock_model_instance
        self.embedding_model = EmbeddingModel()

    def test_init_success(self):
        self.assertEqual(self.embedding_model.model_name, "BAAI/bge-base-en-v1.5")

    def test_generate_embeddings_success(self):
        # Setup mock embeddings returned by the model
        mock_embeddings = [[0.1, 0.2], [0.3, 0.4]]
        self.mock_model_instance.encode.return_value = mock_embeddings

        documents = [
            Document(page_content="Doc 1", metadata={"id": 1}),
            Document(page_content="Doc 2", metadata={"id": 2}),
        ]

        embeddings, valid_docs = self.embedding_model.generate_embeddings(documents)

        # Assert correct methods called on SentenceTransformer
        self.mock_model_instance.encode.assert_called_once_with(
            ["Doc 1", "Doc 2"],
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        # Assert results
        self.assertEqual(embeddings, mock_embeddings)
        self.assertEqual(valid_docs, documents)

    def test_generate_embeddings_skip_empty_docs(self):
        mock_embeddings = [[0.1, 0.2]]
        self.mock_model_instance.encode.return_value = mock_embeddings

        documents = [
            Document(page_content="Doc 1", metadata={"id": 1}),
            Document(page_content="   ", metadata={"id": 2}), # empty content
            Document(page_content="", metadata={"id": 3}),    # empty content
        ]

        embeddings, valid_docs = self.embedding_model.generate_embeddings(documents)

        # Assert only valid docs were passed to encode
        self.mock_model_instance.encode.assert_called_once_with(
            ["Doc 1"],
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        # Assert results contain only valid elements
        self.assertEqual(embeddings, mock_embeddings)
        self.assertEqual(len(valid_docs), 1)
        self.assertEqual(valid_docs[0].page_content, "Doc 1")

    def test_generate_embeddings_all_empty_docs_raises(self):
        documents = [
            Document(page_content="", metadata={"id": 1}),
        ]
        with self.assertRaises(ValueError) as context:
            self.embedding_model.generate_embeddings(documents)
        self.assertIn("No valid documents found for embedding", str(context.exception))

    def test_generate_embeddings_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            self.embedding_model.generate_embeddings("not a list")

        with self.assertRaises(TypeError):
            self.embedding_model.generate_embeddings(["not a document"])

    def test_generate_query_embedding_success(self):
        mock_embedding = [0.1, 0.2, 0.3]
        self.mock_model_instance.encode.return_value = mock_embedding

        result = self.embedding_model.generate_query_embedding("test query")

        self.assertEqual(result, mock_embedding)
        self.mock_model_instance.encode.assert_called_once_with(
            "test query",
            convert_to_numpy=True,
            normalize_embeddings=True
        )

    def test_generate_query_embedding_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            self.embedding_model.generate_query_embedding(123)
        with self.assertRaises(TypeError):
            self.embedding_model.generate_query_embedding(None)

    def test_generate_query_embedding_empty_query_raises(self):
        with self.assertRaises(ValueError):
            self.embedding_model.generate_query_embedding("")
        with self.assertRaises(ValueError):
            self.embedding_model.generate_query_embedding("   ")

    def test_generate_query_embedding_failure_propagates(self):
        self.mock_model_instance.encode.side_effect = RuntimeError("Encoding failed")
        with self.assertRaises(RuntimeError):
            self.embedding_model.generate_query_embedding("test query")

if __name__ == "__main__":
    unittest.main()
