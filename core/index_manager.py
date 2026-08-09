from pathlib import Path
import json
from datetime import datetime, timezone

from config.settings import KNOWLEDGE_BASE_PATH
from utils.logger import get_logger

class IndexManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.registry_dir = KNOWLEDGE_BASE_PATH
        self.registry_file = self.registry_dir / "document_registry.json"
        self.quiz_registry_file = self.registry_dir / "quiz_registry.json"

        self._initialize()

    def _initialize(self):
        try:
            self.registry_dir.mkdir(exist_ok=True)

            if not self.registry_file.exists():
                with open(self.registry_file, "w", encoding="utf-8") as file:
                    json.dump({}, file, indent=4)
                self.logger.info("Created document registry.")
            else:
                self.logger.info("Document registry already exists.")

            if not self.quiz_registry_file.exists():
                with open(self.quiz_registry_file, "w", encoding="utf-8") as file:
                    json.dump({}, file, indent=4)
                self.logger.info("Created quiz registry.")
            else:
                self.logger.info("Quiz registry already exists.")

        except Exception as e:
            self.logger.error(f"Failed to initialize registry: {e}")
            raise

    def load_registry(self):
        try:
            with open(self.registry_file, "r", encoding="utf-8") as file:
                registry = json.load(file)

            self.logger.info("Document registry loaded successfully.")
            return registry

        except Exception as e:
            self.logger.error(f"Failed to load document registry: {e}")
            raise

    def save_registry(self, registry):
        try:
            with open(self.registry_file, "w", encoding="utf-8") as file:
                json.dump(
                    registry,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            self.logger.info("Document registry saved successfully.")

        except Exception as e:
            self.logger.error(f"Failed to save document registry: {e}")
            raise

    def is_document_indexed(self, file_path):
        registry = self.load_registry()
        return str(file_path) in registry

    def register_document(self, file_path, document_id, chunks):
        registry = self.load_registry()

        registry[str(file_path)] = {
            "document_id": document_id,
            "chunks": chunks,
            "indexed_at": datetime.now().astimezone().isoformat(),
            "status": "indexed"
        }

        self.save_registry(registry)
        self.logger.info(f"Registered document: {file_path}")

    def load_quiz_registry(self):
        try:
            with open(self.quiz_registry_file, "r", encoding="utf-8") as file:
                registry = json.load(file)
            self.logger.info("Quiz registry loaded successfully.")
            return registry
        except Exception as e:
            self.logger.error(f"Failed to load quiz registry: {e}")
            return {}

    def save_quiz_registry(self, registry):
        try:
            with open(self.quiz_registry_file, "w", encoding="utf-8") as file:
                json.dump(registry, file, indent=4, ensure_ascii=False)
            self.logger.info("Quiz registry saved successfully.")
        except Exception as e:
            self.logger.error(f"Failed to save quiz registry: {e}")
            raise

    def is_quiz_indexed(self, file_path):
        registry = self.load_quiz_registry()
        return str(file_path) in registry

    def register_quiz_document(self, file_path, document_id, chunks, questions_count=0):
        registry = self.load_quiz_registry()

        registry[str(file_path)] = {
            "document_id": document_id,
            "chunks": chunks,
            "questions_count": questions_count,
            "indexed_at": datetime.now().astimezone().isoformat(),
            "status": "indexed"
        }

        self.save_quiz_registry(registry)
        self.logger.info(f"Registered quiz document: {file_path}")

