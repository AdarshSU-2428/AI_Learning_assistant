import unittest
from unittest.mock import patch, MagicMock
from core.llm_client import LLMClient
from config.settings import LLM_MODEL

class TestLLMClient(unittest.TestCase):
    @patch("core.llm_client.Groq")
    def setUp(self, mock_groq_cls):
        self.mock_groq_instance = MagicMock()
        mock_groq_cls.return_value = self.mock_groq_instance
        
        # Instantiate LLMClient
        self.llm_client = LLMClient()

    def test_init_success(self):
        self.assertIsNotNone(self.llm_client.client)
        self.assertEqual(self.llm_client.model, LLM_MODEL)

    def test_generate_response_success(self):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello AI!"}
        ]
        expected_response = "Hello human!"
        
        # Mock Completion response structure: response.choices[0].message.content
        mock_choice = MagicMock()
        mock_choice.message.content = expected_response
        
        mock_completions = MagicMock()
        mock_completions.choices = [mock_choice]
        
        self.mock_groq_instance.chat.completions.create.return_value = mock_completions

        response = self.llm_client.generate_response(messages)

        self.assertEqual(response, expected_response)
        self.mock_groq_instance.chat.completions.create.assert_called_once_with(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.2,
            max_completion_tokens=1024
        )

    def test_generate_response_invalid_messages_type_raises(self):
        with self.assertRaises(TypeError):
            self.llm_client.generate_response("Not a list")
        with self.assertRaises(TypeError):
            self.llm_client.generate_response(123)
        with self.assertRaises(TypeError):
            self.llm_client.generate_response(None)
        self.mock_groq_instance.chat.completions.create.assert_not_called()

    def test_generate_response_invalid_message_item_type_raises(self):
        with self.assertRaises(TypeError):
            self.llm_client.generate_response([123])
        with self.assertRaises(TypeError):
            self.llm_client.generate_response([None])
        with self.assertRaises(TypeError):
            self.llm_client.generate_response(["not a dict"])
        self.mock_groq_instance.chat.completions.create.assert_not_called()

    def test_generate_response_missing_keys_raises(self):
        with self.assertRaises(ValueError):
            self.llm_client.generate_response([{"role": "user"}])
        with self.assertRaises(ValueError):
            self.llm_client.generate_response([{"content": "hello"}])
        self.mock_groq_instance.chat.completions.create.assert_not_called()

    def test_generate_response_invalid_field_types_raises(self):
        with self.assertRaises(TypeError):
            self.llm_client.generate_response([{"role": 123, "content": "hello"}])
        with self.assertRaises(TypeError):
            self.llm_client.generate_response([{"role": "user", "content": None}])
        self.mock_groq_instance.chat.completions.create.assert_not_called()

    def test_generate_response_invalid_role_raises(self):
        with self.assertRaises(ValueError):
            self.llm_client.generate_response([{"role": "banana", "content": "hello"}])
        with self.assertRaises(ValueError):
            self.llm_client.generate_response([{"role": "SYSTEM", "content": "hello"}])
        self.mock_groq_instance.chat.completions.create.assert_not_called()

    def test_generate_response_empty_values_raises(self):
        with self.assertRaises(ValueError):
            self.llm_client.generate_response([{"role": "", "content": "hello"}])
        with self.assertRaises(ValueError):
            self.llm_client.generate_response([{"role": "user", "content": "   "}])
        self.mock_groq_instance.chat.completions.create.assert_not_called()

    def test_generate_response_exception_propagates(self):
        messages = [{"role": "user", "content": "Will fail"}]
        self.mock_groq_instance.chat.completions.create.side_effect = Exception("API error")
        
        # Directly mock the logger on the instance
        self.llm_client.logger = MagicMock()
        
        with self.assertRaises(Exception):
            self.llm_client.generate_response(messages)

        self.llm_client.logger.exception.assert_called_once_with(f"Failed to generate response from LLM using {LLM_MODEL}.")

if __name__ == "__main__":
    unittest.main()
