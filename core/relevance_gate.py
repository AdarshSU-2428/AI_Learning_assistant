from utils.logger import get_logger
from config.settings import RERANK_SCORE_THRESHOLD


class RelevanceGate:
    def __init__(self, score_threshold=RERANK_SCORE_THRESHOLD):
        self.logger = get_logger(__name__)
        self.score_threshold = score_threshold

    def evaluate_relevance(self, scored_documents, score_threshold=None):
        self.logger.info("Evaluating candidate document relevance...")

        try:
            threshold = score_threshold if score_threshold is not None else self.score_threshold

            if not scored_documents:
                self.logger.info("No scored documents provided to RelevanceGate.")
                return [], False

            top_score = float(scored_documents[0][1])

            # Noise floor threshold (out-of-syllabus baking cake queries score < 0.00001)
            if top_score < 0.00005:
                self.logger.info(f"Top candidate score ({top_score:.6f}) below noise floor. Query rejected.")
                return [], False

            is_ocr_doc = any(
                doc.metadata.get("source_type") == "handwritten_notes"
                or "DMS_" in str(doc.metadata.get("file_name", "")).upper()
                or "OT_" in str(doc.metadata.get("file_name", "")).upper()
                for doc, _ in scored_documents[:5]
            )

            if is_ocr_doc and top_score < 0.20:
                self.logger.info("Handwritten OCR resilience active: Accepting top candidate OCR documents.")
                accepted_documents = [doc for doc, score in scored_documents[:12]]
            elif top_score >= 0.20:
                accepted_documents = [
                    doc for doc, score in scored_documents[:12] if score >= 0.05
                ]
            elif top_score >= 0.001:
                accepted_documents = [
                    doc for doc, score in scored_documents[:12] if score >= 0.001
                ]
            else:
                accepted_documents = []

            if not accepted_documents:
                self.logger.info(f"No documents passed relevance gate (top score: {top_score:.4f}).")
                return [], False

            self.logger.info(f"RelevanceGate accepted {len(accepted_documents)} / {len(scored_documents)} documents (top score: {top_score:.4f}).")

            return accepted_documents, True

        except Exception as e:
            self.logger.error(f"Relevance evaluation failed: {e}")
            raise