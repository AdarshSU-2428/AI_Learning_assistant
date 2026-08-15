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

        path_parts = [p.lower() for p in self.file_path.parts]
        file_lower = self.file_path.name.lower()

        # 1. Determine Content Type
        if "lab" in path_parts:
            content_type = "lab"
        elif "quiz" in path_parts:
            content_type = "quiz"
        elif "exam" in path_parts:
            content_type = "exam"
        else:
            content_type = "notes"

        # 2. Determine Source Type
        if "assignment" in path_parts or "assignment" in file_lower:
            source_type = "lab_assignment"
        elif "manual" in path_parts or "manual" in file_lower or content_type == "lab":
            source_type = "lab_manual"
        elif "ebook" in file_lower or "textbook" in file_lower or "book" in file_lower:
            source_type = "textbook"
        elif content_type == "exam":
            source_type = "pyq_paper"
        elif content_type == "quiz":
            source_type = "quiz_paper"
        else:
            source_type = "college_notes"

        # 3. Determine Subject from Folder Names
        known_subjects = [
            "AI", "Biology", "COA", "DAA", "DBMS", "DEC", 
            "Discrete Maths", "MEE", "OOP Java", "Operating system", "OS",
            "Optimization Techniques", "Python", "IWT"
        ]
        
        subject = "General"
        for part in reversed(self.file_path.parts[:-1]):
            for s in known_subjects:
                if part.lower() == s.lower() or part.lower() == s.lower().replace(" ", "_"):
                    subject = s
                    break
            if subject != "General":
                break

        if subject == "General" and len(self.file_path.parents) > 0:
            parent = self.file_path.parent.name
            if parent.lower() not in ["raw", "data", "documents", "manuals", "assignments", "lab", "notes", "quiz", "exam", "lab assignments", "lab manuals"]:
                subject = parent

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
