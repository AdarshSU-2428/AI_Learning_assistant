from pptx import Presentation

from core.loaders.loader import BaseLoader


class PPTLoader(BaseLoader):
    def extract_text(self):
        self.logger.info(f"Extracting text from {self.file_path.name}")

        try:
            presentation = Presentation(self.file_path)

            units = []

            for slide_num, slide in enumerate(presentation.slides, start=1):
                slide_text = ""
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_text += shape.text + "\n"

                if slide_text and slide_text.strip():
                    units.append(
                        {
                            "text": slide_text,
                            "metadata": {"slide": slide_num},
                        }
                    )

            self.logger.info(f"Successfully extracted text from {len(presentation.slides)} slides.")

            return units

        except Exception as e:
            self.logger.error(f"Error while reading PPT: {e}")
            raise