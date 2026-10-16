import unittest
from unittest.mock import patch, MagicMock
import requests

from frontend.ui.api_client import (
    APIClient,
    APIClientError,
    BackendConnectionError,
    BackendTimeoutError,
    BackendResponseError,
    InvalidBackendResponseError,
)


class TestAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = APIClient(base_url="http://localhost:8000", timeout=5)

    def test_init_defaults(self):
        default_client = APIClient(base_url=None)
        self.assertEqual(default_client.base_url, "http://127.0.0.1:8000")

    def test_init_trailing_slash_strip(self):
        client = APIClient(base_url="http://localhost:8000/")
        self.assertEqual(client.base_url, "http://localhost:8000")

    @patch("frontend.ui.api_client.requests.post")
    def test_send_message_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {
            "query": "What is Python?",
            "answer": "Python is a programming language.",
            "sources": [],
        }
        mock_post.return_value = mock_resp

        res = self.client.send_message("What is Python?")

        self.assertEqual(res["answer"], "Python is a programming language.")
        mock_post.assert_called_once_with(
            "http://localhost:8000/chat",
            json={"query": "What is Python?"},
            timeout=5,
        )

    @patch("frontend.ui.api_client.requests.post")
    def test_send_message_timeout(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout()
        with self.assertRaises(BackendTimeoutError):
            self.client.send_message("Hello")

    @patch("frontend.ui.api_client.requests.post")
    def test_send_message_connection_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError()
        with self.assertRaises(BackendConnectionError):
            self.client.send_message("Hello")

    @patch("frontend.ui.api_client.requests.post")
    def test_send_message_request_exception(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException()
        with self.assertRaises(APIClientError):
            self.client.send_message("Hello")

    @patch("frontend.ui.api_client.requests.post")
    def test_send_message_http_error_with_detail(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 400
        mock_resp.json.return_value = {"detail": "Question cannot be empty."}
        mock_post.return_value = mock_resp

        with self.assertRaises(BackendResponseError) as ctx:
            self.client.send_message("")

        self.assertEqual(str(ctx.exception), "Question cannot be empty.")

    @patch("frontend.ui.api_client.requests.post")
    def test_send_message_http_error_without_detail(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 500
        mock_resp.json.side_effect = ValueError()
        mock_post.return_value = mock_resp

        with self.assertRaises(BackendResponseError) as ctx:
            self.client.send_message("Test")

        self.assertEqual(str(ctx.exception), "Backend returned HTTP 500.")

    @patch("frontend.ui.api_client.requests.post")
    def test_send_message_invalid_json(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.side_effect = requests.exceptions.JSONDecodeError(
            "msg", "doc", 0
        )
        mock_post.return_value = mock_resp

        with self.assertRaises(InvalidBackendResponseError):
            self.client.send_message("Test")

    @patch("frontend.ui.api_client.requests.post")
    def test_send_message_missing_field(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"query": "Q", "answer": "A"}
        mock_post.return_value = mock_resp

        with self.assertRaises(InvalidBackendResponseError):
            self.client.send_message("Q")

    @patch("frontend.ui.api_client.requests.post")
    def test_send_message_empty_answer(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {
            "query": "Q",
            "answer": "   ",
            "sources": [],
        }
        mock_post.return_value = mock_resp

        with self.assertRaises(InvalidBackendResponseError):
            self.client.send_message("Q")

    @patch("frontend.ui.api_client.requests.post")
    def test_generate_quiz_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {
            "topic": "Binary Search",
            "difficulty": "Medium",
            "questions": [{"id": 1, "question": "Q1"}],
            "sources": [],
            "is_relevant": True,
            "message": "Success"
        }
        mock_post.return_value = mock_resp

        res = self.client.generate_quiz("Binary Search", subject="DAA", num_questions=5, difficulty="Medium")

        self.assertEqual(res["topic"], "Binary Search")
        mock_post.assert_called_once_with(
            "http://localhost:8000/quiz/generate",
            json={
                "topic": "Binary Search",
                "subject": "DAA",
                "num_questions": 5,
                "difficulty": "Medium"
            },
            timeout=5,
        )

    @patch("frontend.ui.api_client.requests.post")
    def test_evaluate_quiz_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {
            "score": 5,
            "total": 5,
            "percentage": 100.0,
            "details": []
        }
        mock_post.return_value = mock_resp

        res = self.client.evaluate_quiz([{"id": 1}], {"1": "A"})

        self.assertEqual(res["score"], 5)
        self.assertEqual(res["percentage"], 100.0)
        mock_post.assert_called_once_with(
            "http://localhost:8000/quiz/evaluate",
            json={
                "quiz_questions": [{"id": 1}],
                "user_answers": {"1": "A"}
            },
            timeout=5,
        )

    @patch("frontend.ui.api_client.requests.post")
    def test_send_lab_message_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {
            "query": "Implement SJF",
            "answer": "SJF implementation...",
            "sources": [],
            "is_relevant": True
        }
        mock_post.return_value = mock_resp

        res = self.client.send_lab_message("Implement SJF", subject="OS")

        self.assertEqual(res["answer"], "SJF implementation...")
        self.assertTrue(res["is_relevant"])
        mock_post.assert_called_once_with(
            "http://localhost:8000/lab/chat",
            json={"query": "Implement SJF", "subject": "OS"},
            timeout=5,
        )

    @patch("frontend.ui.api_client.requests.post")
    def test_send_lab_message_error(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 400
        mock_resp.json.return_value = {"detail": "Invalid question"}
        mock_post.return_value = mock_resp

        with self.assertRaises(BackendResponseError):
            self.client.send_lab_message("Bad question")


if __name__ == "__main__":
    unittest.main()
