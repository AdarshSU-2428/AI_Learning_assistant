import os
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from core.loaders.loader import BaseLoader
from core.loaders.pdf_loader import PDFLoader
from core.loaders.ppt_loader import PPTLoader
from core.loaders.docx_loader import DOCXLoader


class DummyLoader(BaseLoader):
    def extract_text(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            return [{"text": file.read(), "metadata": {}}]


class TestBaseLoader(unittest.TestCase):
    def setUp(self):
        self.test_file = Path("test_sample.txt")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("This is a test file.")

        self.test_dir = Path("test_dummy_dir")
        self.test_dir.mkdir(exist_ok=True)

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()
        if self.test_dir.exists():
            self.test_dir.rmdir()

    def test_successful_load(self):
        loader = DummyLoader(self.test_file)
        units = loader.load()

        self.assertEqual(len(units), 1)
        self.assertEqual(units[0]["text"], "This is a test file.")
        self.assertEqual(units[0]["metadata"]["file_name"], "test_sample.txt")
        self.assertEqual(units[0]["metadata"]["file_type"], ".txt")
        self.assertEqual(units[0]["metadata"]["file_path"], "test_sample.txt")

    def test_file_not_found(self):
        loader = DummyLoader("non_existent_file.txt")
        with self.assertRaises(FileNotFoundError):
            loader.load()

    def test_is_directory_error(self):
        loader = DummyLoader(self.test_dir)
        with self.assertRaises(ValueError):
            loader.load()


class TestPDFLoader(unittest.TestCase):
    @patch("core.loaders.pdf_loader.PdfReader")
    def test_pdf_extraction_success(self, mock_pdf_reader):
        mock_page_1 = MagicMock()
        mock_page_1.extract_text.return_value = "Page 1 Text"
        mock_page_2 = MagicMock()
        mock_page_2.extract_text.return_value = "Page 2 Text"

        mock_reader_instance = mock_pdf_reader.return_value
        mock_reader_instance.pages = [mock_page_1, mock_page_2]

        loader = PDFLoader("dummy.pdf")

        with patch.object(loader, "validate_file") as mock_validate:
            units = loader.load()

            self.assertEqual(len(units), 2)
            self.assertEqual(units[0]["text"], "Page 1 Text")
            self.assertEqual(units[0]["metadata"]["page"], 1)
            self.assertEqual(units[0]["metadata"]["file_name"], "dummy.pdf")
            self.assertEqual(units[0]["metadata"]["file_type"], ".pdf")

            self.assertEqual(units[1]["text"], "Page 2 Text")
            self.assertEqual(units[1]["metadata"]["page"], 2)

            mock_validate.assert_called_once()

    @patch("core.loaders.pdf_loader.PdfReader")
    def test_pdf_extraction_failure(self, mock_pdf_reader):
        mock_pdf_reader.side_effect = Exception("Corrupt PDF file")

        loader = PDFLoader("dummy.pdf")

        with patch.object(loader, "validate_file"):
            with self.assertRaises(Exception) as context:
                loader.load()

            self.assertIn("Corrupt PDF file", str(context.exception))


class TestPPTLoader(unittest.TestCase):
    @patch("core.loaders.ppt_loader.Presentation")
    def test_ppt_extraction_success(self, mock_presentation):
        mock_shape_1 = MagicMock()
        mock_shape_1.text = "Slide 1 Content"
        mock_shape_2 = MagicMock()
        mock_shape_2.text = "Slide 2 Content"

        mock_shape_no_text = MagicMock(spec=[])

        mock_slide_1 = MagicMock()
        mock_slide_1.shapes = [mock_shape_1, mock_shape_no_text]
        mock_slide_2 = MagicMock()
        mock_slide_2.shapes = [mock_shape_2]

        mock_pres_instance = mock_presentation.return_value
        mock_pres_instance.slides = [mock_slide_1, mock_slide_2]

        loader = PPTLoader("dummy.pptx")

        with patch.object(loader, "validate_file") as mock_validate:
            units = loader.load()

            self.assertEqual(len(units), 2)
            self.assertEqual(units[0]["text"], "Slide 1 Content\n")
            self.assertEqual(units[0]["metadata"]["slide"], 1)
            self.assertEqual(units[0]["metadata"]["file_name"], "dummy.pptx")
            self.assertEqual(units[0]["metadata"]["file_type"], ".pptx")

            self.assertEqual(units[1]["text"], "Slide 2 Content\n")
            self.assertEqual(units[1]["metadata"]["slide"], 2)

            mock_validate.assert_called_once()

    @patch("core.loaders.ppt_loader.Presentation")
    def test_ppt_extraction_failure(self, mock_presentation):
        mock_presentation.side_effect = Exception("Corrupt PPTX file")

        loader = PPTLoader("dummy.pptx")

        with patch.object(loader, "validate_file"):
            with self.assertRaises(Exception) as context:
                loader.load()

            self.assertIn("Corrupt PPTX file", str(context.exception))


class TestDOCXLoader(unittest.TestCase):
    @patch("core.loaders.docx_loader.Document")
    def test_docx_extraction_success(self, mock_document):
        mock_para_1 = MagicMock()
        mock_para_1.text = "Paragraph 1 Content"
        mock_para_2 = MagicMock()
        mock_para_2.text = "  "
        mock_para_3 = MagicMock()
        mock_para_3.text = "Paragraph 2 Content"

        mock_cell_1 = MagicMock()
        mock_cell_1.text = "Cell 1"
        mock_cell_2 = MagicMock()
        mock_cell_2.text = "Cell 2"

        mock_row_1 = MagicMock()
        mock_row_1.cells = [mock_cell_1, mock_cell_2]

        mock_table_1 = MagicMock()
        mock_table_1.rows = [mock_row_1]

        mock_doc_instance = mock_document.return_value
        mock_doc_instance.paragraphs = [mock_para_1, mock_para_2, mock_para_3]
        mock_doc_instance.tables = [mock_table_1]

        loader = DOCXLoader("dummy.docx")

        with patch.object(loader, "validate_file") as mock_validate:
            units = loader.load()

            expected_text = (
                "Paragraph 1 Content\nParagraph 2 Content\n\nCell 1 | Cell 2\n"
            )
            self.assertEqual(len(units), 1)
            self.assertEqual(units[0]["text"], expected_text)
            self.assertEqual(units[0]["metadata"]["file_name"], "dummy.docx")
            self.assertEqual(units[0]["metadata"]["file_type"], ".docx")

            mock_validate.assert_called_once()

    @patch("core.loaders.docx_loader.Document")
    def test_docx_extraction_failure(self, mock_document):
        mock_document.side_effect = Exception("Corrupt DOCX file")

        loader = DOCXLoader("dummy.docx")

        with patch.object(loader, "validate_file"):
            with self.assertRaises(Exception) as context:
                loader.load()

            self.assertIn("Corrupt DOCX file", str(context.exception))


if __name__ == "__main__":
    unittest.main()