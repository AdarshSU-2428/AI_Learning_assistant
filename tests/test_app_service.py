import unittest
from unittest.mock import patch, MagicMock
from services.app_service import ApplicationService


class TestApplicationService(unittest.TestCase):
    @patch("services.app_service.QuizService")
    @patch("services.app_service.LearningService")
    @patch("services.app_service.IndexingService")
    def setUp(self, mock_indexing_cls, mock_learning_cls, mock_quiz_cls):
        self.mock_learning = MagicMock()
        self.mock_indexing = MagicMock()
        self.mock_quiz = MagicMock()

        mock_learning_cls.return_value = self.mock_learning
        mock_indexing_cls.return_value = self.mock_indexing
        mock_quiz_cls.return_value = self.mock_quiz

        self.service = ApplicationService()

    def test_init(self):
        self.assertEqual(self.service.learning_service, self.mock_learning)
        self.assertEqual(self.service.indexing_service, self.mock_indexing)
        self.assertEqual(self.service.quiz_service, self.mock_quiz)

    def test_index_documents(self):
        self.mock_indexing.index_directory.return_value = {"status": "success"}

        result = self.service.index_documents("dummy/path")

        self.assertEqual(result, {"status": "success"})
        self.mock_indexing.index_directory.assert_called_once_with("dummy/path")

    def test_chat(self):
        self.mock_learning.chat.return_value = {"answer": "result"}

        result = self.service.chat("hello", subject="OS")

        self.assertEqual(result, {"answer": "result"})
        self.mock_learning.chat.assert_called_once_with("hello", subject="OS")

    def test_generate_quiz(self):
        self.mock_quiz.generate_quiz.return_value = {"questions": []}

        result = self.service.generate_quiz("Binary Search", subject="DAA", num_questions=5, difficulty="Medium")

        self.assertEqual(result, {"questions": []})
        self.mock_quiz.generate_quiz.assert_called_once_with(
            topic="Binary Search",
            subject="DAA",
            num_questions=5,
            difficulty="Medium"
        )

    def test_evaluate_quiz_submission(self):
        self.mock_quiz.evaluate_submission.return_value = {"score": 5, "total": 5}

        result = self.service.evaluate_quiz_submission([], {})

        self.assertEqual(result, {"score": 5, "total": 5})
        self.mock_quiz.evaluate_submission.assert_called_once_with(
            quiz_questions=[],
            user_answers={}
        )


if __name__ == "__main__":
    unittest.main()
