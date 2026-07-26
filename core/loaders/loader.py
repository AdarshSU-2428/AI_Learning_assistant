from abc import ABC, abstractmethod
from pathlib import Path
from utils.logger import get_logger


class BaseLoader(ABC):
    def __init__(self, file_path=None):
        self.logger = get_logger(__name__)
        if file_path is not None:
            self.file_path = Path(file_path)

    def validate_file(self):
        if not hasattr(self, "file_path"):
            raise ValueError("file_path has not been set.")

        if not self.file_path.exists():
            self.logger.error(f"File not found: {self.file_path}")
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if not self.file_path.is_file():
            self.logger.error(f"{self.file_path} is not a valid file.")
            raise ValueError(f"{self.file_path} is not a valid file.")

    def create_metadata(self):
        return {
            "file_name": self.file_path.name,
            "file_type": self.file_path.suffix.lower(),
            "file_path": str(self.file_path),
        }

    def load(self, file_path=None):
        if file_path is not None:
            self.file_path = Path(file_path)

        if not hasattr(self, "file_path"):
            raise ValueError("file_path must be provided either in __init__ or load()")

        self.logger.info(f"Loading file: {self.file_path.name}")

        self.validate_file()

        units = self.extract_text()

        common_metadata = self.create_metadata()

        loaded_units = []
        if isinstance(units, list):
            for unit in units:
                if isinstance(unit, dict):
                    text = unit.get("text", "")
                    if text and text.strip():
                        unit_metadata = common_metadata.copy()
                        unit_metadata.update(unit.get("metadata", {}))
                        loaded_units.append(
                            {
                                "text": text,
                                "metadata": unit_metadata,
                            }
                        )

        if not loaded_units:
            self.logger.warning("No text could be extracted.")

        self.logger.info(f"{self.file_path.name} loaded successfully.")

        return loaded_units

    @abstractmethod
    def extract_text(self):
        pass
