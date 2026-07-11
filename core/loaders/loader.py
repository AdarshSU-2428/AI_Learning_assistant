from abc import ABC, abstractclassmethod
from pathlib import Path
from utils.logger import get_logger

class BaseLoader(ABC) :
    def __init__(self, file_path) :
        self.file_path = Path(file_path)
        self.logger = get_logger(__name__)

    def validate_file(self) :
        if not self.file_path.exists() :
            self.logger.error(f"File not found: {self.file_path}")
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if not self.file_path.is_file() :
            self.logger.error(f"{self.file_path} is not a valid file.")
            raise ValueError(f"{self.file_path} is not a valid file.")

    def create_metadata(self) :
        return {
            "file_name" : self.file_path.name,
            "file_type" : self.file_path.suffix.lower(),
            "file_path" : str(self.file_path)
        }

    def load(self) :
        self.logger.info(f"Loading file: {self.file_path.name}")

        self.validate_file()

        text = self.extract_text()

        metadata = self.create_metadata()

        self.logger.info(f"{self.file_path.name} loaded successfully.")

        return text, metadata

    def extract_text(self) :
        pass

