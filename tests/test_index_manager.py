import unittest
import shutil
import json
import time
from pathlib import Path
from datetime import datetime

from core.index_manager import IndexManager
from config.settings import KNOWLEDGE_BASE_PATH

def safe_rmtree(path):
    path = Path(path)
    for _ in range(5):
        try:
            if path.exists():
                shutil.rmtree(path)
            return
        except PermissionError:
            time.sleep(0.1)
    if path.exists():
        shutil.rmtree(path)

class TestIndexManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_dir = KNOWLEDGE_BASE_PATH
        cls.backup_dir = KNOWLEDGE_BASE_PATH.parent / "knowledge_base_backup"
        # Back up existing knowledge_base folder if it exists
        if cls.db_dir.exists():
            safe_rmtree(cls.backup_dir)
            cls.db_dir.rename(cls.backup_dir)

    @classmethod
    def tearDownClass(cls):
        # Restore backed up knowledge_base folder
        safe_rmtree(cls.db_dir)
        if cls.backup_dir.exists():
            cls.backup_dir.rename(cls.db_dir)

    def setUp(self):
        # Ensure a clean slate for each test case
        safe_rmtree(self.db_dir)
        self.registry_file = self.db_dir / "document_registry.json"

    def tearDown(self):
        # Clean up files created by the test
        safe_rmtree(self.db_dir)

    # --- Initialization Tests ---

    def test_fresh_initialization(self):
        # Action
        manager = IndexManager()
        
        # Expected
        self.assertTrue(self.db_dir.is_dir())
        self.assertTrue(self.registry_file.is_file())
        with open(self.registry_file, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertEqual(content, {})

    def test_existing_registry(self):
        # Precondition
        self.db_dir.mkdir(parents=True, exist_ok=True)
        existing_data = {"dummy.pdf": {"document_id": "doc_001"}}
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4)

        # Action
        manager = IndexManager()

        # Expected
        self.assertTrue(self.registry_file.is_file())
        with open(self.registry_file, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertEqual(content, existing_data)

    def test_missing_registry_file(self):
        # Precondition: Directory exists but registry file does not
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        # Action
        manager = IndexManager()

        # Expected
        self.assertTrue(self.registry_file.is_file())
        with open(self.registry_file, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertEqual(content, {})

    # --- Loading Tests ---

    def test_load_empty_registry(self):
        # Precondition
        manager = IndexManager()  # creates empty registry
        
        # Action
        registry = manager.load_registry()

        # Expected
        self.assertEqual(registry, {})
        self.assertIsInstance(registry, dict)

    def test_load_registry_with_data(self):
        # Precondition
        self.db_dir.mkdir(parents=True, exist_ok=True)
        existing_data = {
            "data/Operating_System/notes.pdf": {
                "document_id": "doc_001",
                "chunks": 120,
                "indexed_at": "2026-07-20T09:30:15",
                "status": "indexed"
            }
        }
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4)

        # Action
        manager = IndexManager()
        registry = manager.load_registry()

        # Expected
        self.assertEqual(registry, existing_data)

    def test_load_corrupted_json_raises_exception(self):
        # Precondition
        self.db_dir.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, "w", encoding="utf-8") as f:
            f.write("{invalid json")

        # Action & Expected
        manager = IndexManager()
        with self.assertRaises(Exception):
            manager.load_registry()

    # --- Saving Tests ---

    def test_save_empty_registry(self):
        # Action
        manager = IndexManager()
        manager.save_registry({})

        # Expected
        with open(self.registry_file, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertEqual(content, {})

    def test_save_one_document(self):
        # Precondition
        manager = IndexManager()
        registry = {
            "data/Operating_System/notes.pdf": {
                "document_id": "doc_001",
                "chunks": 120,
                "indexed_at": "2026-07-20T09:30:15",
                "status": "indexed"
            }
        }

        # Action
        manager.save_registry(registry)

        # Expected
        with open(self.registry_file, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertEqual(content, registry)

    def test_verify_persistence(self):
        # Precondition
        manager = IndexManager()
        registry = {
            "data/Operating_System/notes.pdf": {
                "document_id": "doc_001",
                "chunks": 120,
                "indexed_at": "2026-07-20T09:30:15",
                "status": "indexed"
            }
        }

        # Action
        manager.save_registry(registry)
        loaded = manager.load_registry()

        # Expected
        self.assertEqual(loaded, registry)

    def test_save_updated_registry(self):
        # Precondition
        self.db_dir.mkdir(parents=True, exist_ok=True)
        initial_data = {
            "data/Operating_System/OS_Notes.pdf": {
                "document_id": "doc_001",
                "chunks": 120,
                "indexed_at": "2026-07-20T09:30:15",
                "status": "indexed"
            }
        }
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=4)

        # Action
        manager = IndexManager()
        registry = manager.load_registry()
        registry["data/DBMS/DBMS_Notes.pdf"] = {
            "document_id": "doc_002",
            "chunks": 95,
            "indexed_at": "2026-07-20T10:15:00",
            "status": "indexed"
        }
        manager.save_registry(registry)

        # Expected
        with open(self.registry_file, "r", encoding="utf-8") as f:
            content = json.load(f)

        expected_data = {
            "data/Operating_System/OS_Notes.pdf": {
                "document_id": "doc_001",
                "chunks": 120,
                "indexed_at": "2026-07-20T09:30:15",
                "status": "indexed"
            },
            "data/DBMS/DBMS_Notes.pdf": {
                "document_id": "doc_002",
                "chunks": 95,
                "indexed_at": "2026-07-20T10:15:00",
                "status": "indexed"
            }
        }
        self.assertEqual(content, expected_data)

    # --- Document Indexed Checks ---

    def test_is_document_indexed_exists(self):
        # Precondition
        self.db_dir.mkdir(parents=True, exist_ok=True)
        initial_data = {"data/Operating_System/OS_Notes.pdf": {"document_id": "doc_001"}}
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=4)

        # Action & Expected
        manager = IndexManager()
        self.assertTrue(manager.is_document_indexed("data/Operating_System/OS_Notes.pdf"))

    def test_is_document_indexed_does_not_exist(self):
        # Precondition
        self.db_dir.mkdir(parents=True, exist_ok=True)
        initial_data = {"data/Operating_System/OS_Notes.pdf": {"document_id": "doc_001"}}
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=4)

        # Action & Expected
        manager = IndexManager()
        self.assertFalse(manager.is_document_indexed("data/DBMS/DBMS_Notes.pdf"))

    def test_is_document_indexed_empty_registry(self):
        # Precondition
        manager = IndexManager()

        # Action & Expected
        self.assertFalse(manager.is_document_indexed("data/Operating_System/OS_Notes.pdf"))

    # --- Document Registration ---

    def test_register_first_document(self):
        # Precondition
        manager = IndexManager()

        # Action
        manager.register_document(
            file_path="data/Operating_System/OS_Notes.pdf",
            document_id="doc_001",
            chunks=120
        )

        # Expected
        with open(self.registry_file, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertIn("data/Operating_System/OS_Notes.pdf", content)
        doc_info = content["data/Operating_System/OS_Notes.pdf"]
        self.assertEqual(doc_info["document_id"], "doc_001")
        self.assertEqual(doc_info["chunks"], 120)
        self.assertIn("indexed_at", doc_info)
        self.assertEqual(doc_info["status"], "indexed")

    def test_register_second_document(self):
        # Precondition
        manager = IndexManager()
        manager.register_document(
            file_path="data/Operating_System/OS_Notes.pdf",
            document_id="doc_001",
            chunks=120
        )

        # Action
        manager.register_document(
            file_path="data/DBMS/DBMS_Notes.pdf",
            document_id="doc_002",
            chunks=95
        )

        # Expected
        with open(self.registry_file, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertIn("data/Operating_System/OS_Notes.pdf", content)
        self.assertIn("data/DBMS/DBMS_Notes.pdf", content)
        self.assertEqual(content["data/DBMS/DBMS_Notes.pdf"]["document_id"], "doc_002")

    def test_register_existing_document_again_overwrites(self):
        # Precondition
        manager = IndexManager()
        manager.register_document(
            file_path="data/Operating_System/OS_Notes.pdf",
            document_id="doc_001",
            chunks=120
        )

        # Action
        manager.register_document(
            file_path="data/Operating_System/OS_Notes.pdf",
            document_id="doc_999",
            chunks=150
        )

        # Expected
        with open(self.registry_file, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertEqual(len(content), 1)
        self.assertEqual(content["data/Operating_System/OS_Notes.pdf"]["document_id"], "doc_999")
        self.assertEqual(content["data/Operating_System/OS_Notes.pdf"]["chunks"], 150)

if __name__ == "__main__":
    unittest.main()
