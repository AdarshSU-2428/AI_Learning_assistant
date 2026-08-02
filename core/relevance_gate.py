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

            effective_threshold = 0.20 if top_score >= 0.20 else threshold

            accepted_documents = [
                doc for doc, score in scored_documents if score >= effective_threshold
            ]

            if not accepted_documents:
                self.logger.info(f"No documents passed relevance gate (top score: {top_score:.4f}, threshold: {effective_threshold:.4f}).")
                return [], False

            self.logger.info(f"RelevanceGate accepted {len(accepted_documents)} / {len(scored_documents)} documents (top score: {top_score:.4f}).")

            return accepted_documents, True

        except Exception as e:
            self.logger.error(f"Relevance evaluation failed: {e}")
            raise