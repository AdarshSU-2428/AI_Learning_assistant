import unittest
from core.preprocesser import Preprocessor

class TestPreprocessor(unittest.TestCase):
    def setUp(self):
        self.preprocessor = Preprocessor()

    def test_normalize_quotes(self):
        text = "He said \u201chello\u201d, it\u2019s an em\u2014dash."
        result = self.preprocessor._normalize_quotes(text)
        self.assertEqual(result, "He said \"hello\", it's an em-dash.")

    def test_remove_extra_spaces(self):
        text = "Hello    world \t  with   spaces."
        result = self.preprocessor._remove_extra_spaces(text)
        self.assertEqual(result, "Hello world with spaces.")

    def test_remove_extra_blank_lines(self):
        # Test standardizing newlines and collapsing multiple blank lines
        text = "Line 1\r\n\r\n\r\nLine 2\r\rLine 3\n\n\n\nLine 4"
        result = self.preprocessor._remove_extra_blank_lines(text)
        self.assertEqual(result, "Line 1\n\nLine 2\n\nLine 3\n\nLine 4")

    def test_clean_text(self):
        # clean_text now only strips the start and end of the entire string
        text = "  Line 1\n  Line 2  "
        result = self.preprocessor._clean_text(text)
        self.assertEqual(result, "Line 1\n  Line 2")

    def test_preprocess_success(self):
        # Test preprocess end-to-end
        text = "  \u201cMachine  Learning\u201d   \r\n\r\n\r\n   is   amazing.  "
        metadata = {"source": "test"}
        cleaned_text, cleaned_metadata = self.preprocessor.preprocess(text, metadata)
        
        # Trace of execution:
        # 1. _normalize_quotes: "  \"Machine  Learning\"   \r\n\r\n\r\n   is   amazing.  "
        # 2. _remove_extra_spaces: " \"Machine Learning\" \r\n\r\n\r\n is amazing. "
        # 3. _remove_extra_blank_lines: " \"Machine Learning\" \n\n\n is amazing. " -> " \"Machine Learning\" \n\n is amazing. "
        # 4. _clean_text: "\"Machine Learning\" \n\n is amazing."
        self.assertEqual(cleaned_text, "\"Machine Learning\" \n\n is amazing.")
        self.assertEqual(cleaned_metadata, metadata)

    def test_preprocess_invalid_type(self):
        metadata = {"source": "test"}
        with self.assertRaises(TypeError):
            self.preprocessor.preprocess(12345, metadata)

if __name__ == "__main__":
    unittest.main()
