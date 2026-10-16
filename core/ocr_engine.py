import io
import numpy as np
from PIL import Image
from utils.logger import get_logger
import easyocr
from rapidocr_onnxruntime import RapidOCR


class OCREngine:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.rapid_engine = None
        self.easy_reader = None

        try:
            self.rapid_engine = RapidOCR()
            self.logger.info("Initialized RapidOCR (PP-OCRv4 ONNX) engine.")
        except Exception as e:
            self.logger.warning(f"Could not initialize RapidOCR: {e}")

        if self.rapid_engine is None:
            try:
                self.easy_reader = easyocr.Reader(['en'], gpu=False)
                self.logger.info("Initialized EasyOCR reader fallback.")
            except Exception as e:
                self.logger.error(f"Could not initialize EasyOCR: {e}")

    def extract_text_from_image(self, image_input):
        try:
            if isinstance(image_input, (bytes, bytearray)):
                pil_img = Image.open(io.BytesIO(image_input)).convert("RGB")
                np_img = np.array(pil_img)
            elif isinstance(image_input, Image.Image):
                np_img = np.array(image_input.convert("RGB"))
            elif isinstance(image_input, np.ndarray):
                np_img = image_input
            else:
                raise ValueError(f"Unsupported image input type: {type(image_input)}")

            if self.rapid_engine:
                result, _ = self.rapid_engine(np_img)

                if result:
                    lines = [line[1] for line in result if line and len(line) > 1]
                    return " ".join(lines).strip()

                return ""

            elif self.easy_reader:
                results = self.easy_reader.readtext(np_img, detail=0)
                
                return " ".join(results).strip()

            return ""

        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return ""
