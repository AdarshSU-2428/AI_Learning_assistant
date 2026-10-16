from pypdf import PdfReader
from core.loaders.loader import BaseLoader
from core.metadata import create_document_metadata
from core.ocr_engine import OCREngine
from config.settings import PDF_SLIDE_WINDOW_SIZE


class PDFLoader(BaseLoader):
    def __init__(self, file_path=None, window_size=PDF_SLIDE_WINDOW_SIZE):
        super().__init__(file_path)
        self.window_size = window_size
        self.ocr_engine = OCREngine()

    def extract_text(self):
        self.logger.info(f"Extracting text from {self.file_path.name}")

        try:
            reader = PdfReader(self.file_path)
            raw_pages = []

            subject, content_type, source_type = self.infer_metadata_attributes()

            # Pass 1: Extract standard digital text
            digital_pages = []
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                clean_text = page_text.strip()
                if clean_text.lower() == "scanned by camscanner":
                    clean_text = ""
                digital_pages.append((page_num, clean_text, page))

            total_digital_words = sum(len(txt.split()) for _, txt, _ in digital_pages)
            avg_digital_words = total_digital_words / len(digital_pages) if digital_pages else 0

            # Pass 2: Trigger OCR if the document is scanned or handwritten (avg words < 40)
            is_scanned_pdf = avg_digital_words < 40
            if is_scanned_pdf and content_type == "notes":
                source_type = "handwritten_notes"

            for page_num, clean_text, page in digital_pages:
                if is_scanned_pdf:
                    if hasattr(page, "images") and page.images:
                        ocr_parts = []
                        for img in page.images:
                            ocr_txt = self.ocr_engine.extract_text_from_image(img.data)
                            if ocr_txt:
                                ocr_parts.append(ocr_txt)
                        if ocr_parts:
                            clean_text = "\n".join(ocr_parts).strip()
                            self.logger.info(f"OCR extracted {len(clean_text.split())} words from page {page_num} of {self.file_path.name}")

                if clean_text:
                    raw_pages.append((page_num, clean_text))

            units = []
            if not raw_pages:
                self.logger.warning(f"No readable text could be extracted from {self.file_path.name}")
                return units

            total_words = sum(len(txt.split()) for _, txt in raw_pages)
            avg_words = total_words / len(raw_pages) if raw_pages else 0

            if avg_words < 150 and len(raw_pages) > 1:
                for i in range(len(raw_pages)):
                    window = raw_pages[i : i + self.window_size]
                    combined_text = "\n\n".join(
                        f"[Slide {p}]:\n{txt}" for p, txt in window
                    )
                    start_p = window[0][0]
                    end_p = window[-1][0]
                    page_meta = (
                        start_p if start_p == end_p else f"{start_p}-{end_p}"
                    )

                    meta = create_document_metadata(
                        file_name=self.file_path.name,
                        file_path=str(self.file_path),
                        page=page_meta,
                        slide=page_meta,
                        subject=subject,
                        content_type=content_type,
                        source_type=source_type
                    )

                    units.append(
                        {
                            "text": combined_text,
                            "metadata": meta,
                        }
                    )
            else:
                for page_num, page_text in raw_pages:
                    meta = create_document_metadata(
                        file_name=self.file_path.name,
                        file_path=str(self.file_path),
                        page=page_num,
                        subject=subject,
                        content_type=content_type,
                        source_type=source_type
                    )

                    units.append(
                        {
                            "text": page_text,
                            "metadata": meta,
                        }
                    )

            self.logger.info(f"Successfully extracted {len(units)} units from {len(reader.pages)} pages (subject: {subject}, content_type: {content_type}, source_type: {source_type}, avg words/page: {avg_words:.1f}).")

            return units

        except Exception as e:
            self.logger.error(f"Error while reading PDF: {e}")
            raise
