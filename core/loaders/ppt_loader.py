from pptx import Presentation

from core.loaders.loader import BaseLoader

class PPTLoader(BaseLoader):
    def extract_text(self) :
        self.logger.info(f"Extracting text from {self.file_path.name}")

        try:
            presentation = Presentation(self.file_path)

            text = ""

            for slide in presentation.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        text += shape.text + "\n"

            self.logger.info( f"Successfully extracted text from {len(presentation.slides)} slides.")

            return text

        except Exception as e:
            self.logger.error(f"Error while reading PPT: {e}")
            raise