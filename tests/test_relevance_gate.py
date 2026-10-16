import unittest
from langchain_core.documents import Document
from core.relevance_gate import RelevanceGate


class TestRelevanceGate(unittest.TestCase):
    def setUp(self):
        self.gate = RelevanceGate()

    def test_evaluate_relevance_empty_documents(self):
        docs, is_relevant = self.gate.evaluate_relevance([])
        self.assertEqual(docs, [])
        self.assertFalse(is_relevant)

    def test_evaluate_relevance_high_score_accepted(self):
        doc1 = Document(page_content="good doc", metadata={"file_name": "good.pdf"})
        doc2 = Document(page_content="borderline doc", metadata={"file_name": "borderline.pdf"})
        doc3 = Document(page_content="bad doc", metadata={"file_name": "bad.pdf"})

        scored_docs = [(doc1, 0.85), (doc2, 0.30), (doc3, 0.01)]
        docs, is_relevant = self.gate.evaluate_relevance(scored_docs)

        self.assertTrue(is_relevant)
        self.assertEqual(len(docs), 2)
        self.assertEqual(docs[0].page_content, "good doc")
        self.assertEqual(docs[1].page_content, "borderline doc")

    def test_evaluate_relevance_viva_score_tier_accepted(self):
        doc1 = Document(page_content="viva scheduling doc", metadata={"file_name": "OS_Lab_Manual.pdf"})
        doc2 = Document(page_content="viva fcfs doc", metadata={"file_name": "OS_Lab_Manual.pdf"})

        scored_docs = [(doc1, 0.0002), (doc2, 0.0001)]
        docs, is_relevant = self.gate.evaluate_relevance(scored_docs)

        self.assertTrue(is_relevant)
        self.assertEqual(len(docs), 2)
        self.assertEqual(docs[0].page_content, "viva scheduling doc")

    def test_evaluate_relevance_handwritten_ocr_resilience(self):
        doc1 = Document(page_content="ocr formula", metadata={"source_type": "handwritten_notes", "file_name": "OT_Notes.pdf"})
        scored_docs = [(doc1, 0.015)]

        docs, is_relevant = self.gate.evaluate_relevance(scored_docs)
        self.assertTrue(is_relevant)
        self.assertEqual(len(docs), 1)

    def test_evaluate_relevance_out_of_syllabus_refusal(self):
        doc1 = Document(page_content="irrelevant doc 1")
        doc2 = Document(page_content="irrelevant doc 2")

        scored_docs = [(doc1, 0.00001), (doc2, 0.000001)]
        docs, is_relevant = self.gate.evaluate_relevance(scored_docs)

        self.assertFalse(is_relevant)
        self.assertEqual(docs, [])


if __name__ == "__main__":
    unittest.main()
