import unittest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from core.vector_store import VectorStore


class TestVectorStore(unittest.TestCase):
    @patch("core.vector_store.chromadb.PersistentClient")
    def setUp(self, mock_client_cls):
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()

        mock_client_cls.return_value = self.mock_client
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

        self.vector_store = VectorStore(persist_directory="dummy_dir", collection_name="dummy_col")

    def test_init_success(self):
        self.mock_client.get_or_create_collection.assert_called_once_with(name="dummy_col")

    def test_store_success(self):
        documents = [
            Document(page_content="Text 1", metadata={"source": "doc1"}),
            Document(page_content="Text 2", metadata={"source": "doc2"}),
        ]
        import numpy as np
        embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])

        stored_count = self.vector_store.store(documents, embeddings)

        # Assert correct count returned
        self.assertEqual(stored_count, 2)

        # Verify collection.add was called correctly
        self.mock_collection.add.assert_called_once()
        _, kwargs = self.mock_collection.add.call_args

        self.assertEqual(len(kwargs["ids"]), 2)
        self.assertEqual(kwargs["documents"], ["Text 1", "Text 2"])
        self.assertEqual(kwargs["embeddings"], [[0.1, 0.2], [0.3, 0.4]])
        self.assertEqual(kwargs["metadatas"], [{"source": "doc1"}, {"source": "doc2"}])

    def test_store_empty_documents(self):
        stored_count = self.vector_store.store([], [])
        self.assertEqual(stored_count, 0)
        self.mock_collection.add.assert_not_called()

    def test_store_mismatch_length_raises(self):
        documents = [Document(page_content="Text 1")]
        embeddings = [[0.1, 0.2], [0.3, 0.4]]  # length 2

        with self.assertRaises(ValueError):
            self.vector_store.store(documents, embeddings)

    def test_similarity_search_success(self):
        import numpy as np
        query_embedding = np.array([0.1, 0.2])

        # Mock the results returned by chromadb query
        self.mock_collection.query.return_value = {
            "documents": [["Retrieved text 1", "Retrieved text 2"]],
            "metadatas": [[{"source": "doc1"}, {"source": "doc2"}]]
        }

        results = self.vector_store.similarity_search(query_embedding, top_k=2)

        self.mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2]],
            n_results=2
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].page_content, "Retrieved text 1")
        self.assertEqual(results[0].metadata, {"source": "doc1"})
        self.assertEqual(results[1].page_content, "Retrieved text 2")
        self.assertEqual(results[1].metadata, {"source": "doc2"})

    def test_similarity_search_with_where_filter(self):
        import numpy as np
        query_embedding = np.array([0.1, 0.2])

        self.mock_collection.query.return_value = {
            "documents": [["Filtered DBMS text"]],
            "metadatas": [[{"subject": "DBMS", "content_type": "notes"}]]
        }

        where_filter = {"$and": [{"subject": "DBMS"}, {"content_type": "notes"}]}
        results = self.vector_store.similarity_search(query_embedding, top_k=1, where=where_filter)

        self.mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2]],
            n_results=1,
            where=where_filter
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].page_content, "Filtered DBMS text")
        self.assertEqual(results[0].metadata, {"subject": "DBMS", "content_type": "notes"})

    def test_similarity_search_invalid_top_k_raises(self):
        import numpy as np
        query_embedding = np.array([0.1, 0.2])

        with self.assertRaises(ValueError):
            self.vector_store.similarity_search(query_embedding, top_k=0)
        with self.assertRaises(ValueError):
            self.vector_store.similarity_search(query_embedding, top_k=-5)

    def test_similarity_search_none_query_embedding_raises(self):
        with self.assertRaises(ValueError):
            self.vector_store.similarity_search(None, top_k=2)

    def test_similarity_search_failure_propagates(self):
        import numpy as np
        query_embedding = np.array([0.1, 0.2])
        self.mock_collection.query.side_effect = RuntimeError("Query failed")

        with self.assertRaises(RuntimeError):
            self.vector_store.similarity_search(query_embedding, top_k=2)


if __name__ == "__main__":
    unittest.main()
