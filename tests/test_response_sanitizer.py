import unittest
from core.response_sanitizer import ResponseSanitizer

class TestResponseSanitizer(unittest.TestCase):
    def test_clean_empty_response(self):
        self.assertEqual(ResponseSanitizer.clean(""), "")
        self.assertEqual(ResponseSanitizer.clean(None), "")

    def test_clean_no_think_block(self):
        text = "Hello! This is a clean response."
        self.assertEqual(ResponseSanitizer.clean(text), text)

    def test_clean_with_think_block(self):
        text = "<think>\nThinking about the concept of arrays...\n</think>\nAn array is a data structure."
        expected = "An array is a data structure."
        self.assertEqual(ResponseSanitizer.clean(text), expected)

    def test_clean_case_insensitive_think_block(self):
        text = "<THINK>Capitalized thinking...</THINK>Normal output."
        expected = "Normal output."
        self.assertEqual(ResponseSanitizer.clean(text), expected)

    def test_clean_nested_whitespace_strip(self):
        text = "   <think>Thinking...</think>   Clean answer.   "
        expected = "Clean answer."
        self.assertEqual(ResponseSanitizer.clean(text), expected)

    def test_clean_missing_closing_tag(self):
        text = "<think>Thinking... but got cut off"
        expected = ""
        self.assertEqual(ResponseSanitizer.clean(text), expected)

if __name__ == "__main__":
    unittest.main()
