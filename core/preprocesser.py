import re

from utils.logger import get_logger


class Preprocessor:
    def __init__(self):
        self.logger = get_logger(__name__)

    def _normalize_quotes(self, text):
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u2013", "-").replace("\u2014", "-")
        return text

    def _remove_extra_spaces(self, text):
        return re.sub(r"[ \t]+", " ", text)

    def _remove_extra_blank_lines(self, text):
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        return re.sub(r"\n\s*\n+", "\n\n", text)

    def _clean_text(self, text):
        return text.strip()

    def preprocess(self, text, metadata):
        self.logger.info("Starting preprocessing...")

        try:
            if not isinstance(text, str):
                raise TypeError("Input text must be a string.")

            text = self._normalize_quotes(text)
            text = self._remove_extra_spaces(text)
            text = self._remove_extra_blank_lines(text)
            text = self._clean_text(text)

            self.logger.info("Preprocessing completed successfully.")

            return text, metadata

        except Exception as e:
            self.logger.error(f"Preprocessing failed: {e}")
            raise