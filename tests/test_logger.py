import os
import shutil
import logging
import unittest
from utils.logger import get_logger

class TestLogger(unittest.TestCase):
    def setUp(self):
        """Ensure the logs directory is clean before each test."""
        logging.shutdown()
        if os.path.exists("logs"):
            shutil.rmtree("logs")

    def tearDown(self):
        """Ensure the logs directory is clean after each test."""
        logging.shutdown()
        if os.path.exists("logs"):
            shutil.rmtree("logs")

    def test_logger_initialization(self):
        logger = get_logger("test_logger")
        
        # Check level is INFO
        self.assertEqual(logger.level, logging.INFO)
        
        # Check both StreamHandler and FileHandler are added
        self.assertEqual(len(logger.handlers), 2)
        
        # Check folder and file are created
        self.assertTrue(os.path.exists("logs"))
        self.assertTrue(os.path.exists("logs/application.log"))

    def test_no_duplicate_handlers(self):
        logger1 = get_logger("duplicate_test")
        logger2 = get_logger("duplicate_test")
        
        # Retrieving the logger again should reuse the same handlers (should still be 2)
        self.assertEqual(len(logger2.handlers), 2)

if __name__ == "__main__":
    unittest.main()
