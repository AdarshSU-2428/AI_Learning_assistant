from abc import ABC, abstractmethod
from pathlib import Path

from utils.logger import get_logger
from core.metadata import normalize_metadata, create_document_metadata


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

    def infer_metadata_attributes(self):
        if not hasattr(self, "file_path") or self.file_path is None:
            return "General", "notes", "college_notes"

        parent_name = self.file_path.parent.name
        grandparent_name = self.file_path.parent.parent.name if len(self.file_path.parents) > 1 else ""

        subject = parent_name if parent_name.lower() not in ["raw", "data", "documents"] else "General"
        content_type = grandparent_name.lower() if grandparent_name.lower() in ["notes", "quiz", "exam", "lab"] else "notes"

        if parent_name.lower() in ["notes", "quiz", "exam", "lab"]:
            content_type = parent_name.lower()

        file_lower = self.file_path.name.lower()
        if "ebook" in file_lower or "textbook" in file_lower or "book" in file_lower:
            source_type = "textbook"
        elif content_type == "lab":
            source_type = "lab_manual"
        elif content_type == "exam":
            source_type = "pyq_paper"
        elif content_type == "quiz":
            source_type = "quiz_paper"
        else:
            source_type = "college_notes"

        return subject, content_type, source_type

    def load(self, file_path=None):
        if file_path is not None:
            self.file_path = Path(file_path)

        if not hasattr(self, "file_path"):
            raise ValueError("file_path must be provided either in __init__ or load()")

        self.logger.info(f"Loading file: {self.file_path.name}")

        self.validate_file()

        units = self.extract_text()

        loaded_units = []
        if isinstance(units, list):
            for unit in units:
                if isinstance(unit, dict):
                    text = unit.get("text", "")
                    if text and text.strip():
                
                        unit_metadata = normalize_metadata(unit.get("metadata", {}))
                        unit_metadata["file_name"] = self.file_path.name
                        unit_metadata["file_path"] = str(self.file_path)
                        unit_metadata["file_type"] = self.file_path.suffix.lower()

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
