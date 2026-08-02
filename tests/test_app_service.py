import unittest
from unittest.mock import patch, MagicMock
from services.app_service import ApplicationService


class TestApplicationService(unittest.TestCase):
    @patch("services.app_service.LearningService")
    @patch("services.app_service.IndexingService")
    def setUp(self, mock_indexing_cls, mock_learning_cls):
        self.mock_learning = MagicMock()
        self.mock_indexing = MagicMock()

        mock_learning_cls.return_value = self.mock_learning
        mock_indexing_cls.return_value = self.mock_indexing

        self.service = ApplicationService()

    def test_init(self):
        self.assertEqual(self.service.learning_service, self.mock_learning)
        self.assertEqual(self.service.indexing_service, self.mock_indexing)

    def test_index_documents(self):
        self.mock_indexing.index_directory.return_value = {"status": "success"}

        result = self.service.index_documents("dummy/path")

        self.assertEqual(result, {"status": "success"})
        self.mock_indexing.index_directory.assert_called_once_with("dummy/path")

    def test_chat(self):
        self.mock_learning.chat.return_value = {"answer": "result"}

        result = self.service.chat("hello")

        self.assertEqual(result, {"answer": "result"})
        self.mock_learning.chat.assert_called_once_with("hello", subject=None)


if __name__ == "__main__":
    unittest.main()
