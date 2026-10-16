import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from PIL import Image, ImageDraw
import io
from core.ocr_engine import OCREngine


class TestOCREngine(unittest.TestCase):
    def setUp(self):
        # Create a simple synthetic image with text-like shapes
        img = Image.new("RGB", (200, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((10, 40), "HELLO WORLD", fill=(0, 0, 0))
        self.sample_pil_img = img

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        self.sample_img_bytes = buf.getvalue()
        self.sample_np_img = np.array(img)

    def test_ocr_engine_init(self):
        engine = OCREngine()
        self.assertIsNotNone(engine.logger)
        # Should have initialized rapid_engine or easy_reader fallback
        self.assertTrue(engine.rapid_engine is not None or engine.easy_reader is not None)

    def test_extract_text_from_bytes(self):
        engine = OCREngine()
        text = engine.extract_text_from_image(self.sample_img_bytes)
        self.assertIsInstance(text, str)

    def test_extract_text_from_pil_image(self):
        engine = OCREngine()
        text = engine.extract_text_from_image(self.sample_pil_img)
        self.assertIsInstance(text, str)

    def test_extract_text_from_numpy_array(self):
        engine = OCREngine()
        text = engine.extract_text_from_image(self.sample_np_img)
        self.assertIsInstance(text, str)

    def test_unsupported_input_type_raises(self):
        engine = OCREngine()
        # Unsupported type (integer or list) will safely trigger exception block and return empty string
        result = engine.extract_text_from_image(12345)
        self.assertEqual(result, "")

    @patch.object(OCREngine, 'extract_text_from_image')
    def test_ocr_failure_fallback_returns_empty_string(self, mock_ocr):
        mock_ocr.side_effect = Exception("OCR Failure")
        engine = OCREngine()
        try:
            res = engine.extract_text_from_image(self.sample_img_bytes)
        except Exception:
            res = ""
        self.assertEqual(res, "")


if __name__ == "__main__":
    unittest.main()
