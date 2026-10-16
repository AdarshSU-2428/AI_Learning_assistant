import pytest
from services.exam_service import ExamService

def test_clean_and_parse_json_valid():
    service = ExamService.__new__(ExamService)
    raw = '{"exam_title": "Test", "questions": [{"id": 1, "question_text": "Define DAG", "model_answer": "Directed Acyclic Graph", "marks": 1}]}'
    parsed = service._clean_and_parse_json(raw)
    assert parsed is not None
    questions = service._extract_questions(parsed)
    assert len(questions) == 1
    assert questions[0]["question_text"] == "Define DAG"

def test_clean_and_parse_json_with_latex_escapes():
    service = ExamService.__new__(ExamService)
    # \Theta and \log and \frac would break standard json.loads without escape repair
    raw = r'{"questions": [{"id": 1, "question_text": "What is \Theta(n \log n)?", "model_answer": "Use \frac{a}{b} and \sum_{i=1}^n x_i.", "marks": 3}]}'
    parsed = service._clean_and_parse_json(raw)
    assert parsed is not None
    questions = service._extract_questions(parsed)
    assert len(questions) == 1
    assert r"\Theta" in questions[0]["question_text"]

def test_clean_and_parse_json_list_format():
    service = ExamService.__new__(ExamService)
    raw = '[{"id": 1, "question_text": "Explain QuickSort", "model_answer": "Divide and conquer", "marks": 5}]'
    parsed = service._clean_and_parse_json(raw)
    assert parsed is not None
    questions = service._extract_questions(parsed)
    assert len(questions) == 1
    assert questions[0]["marks"] == 5

def test_clean_and_parse_json_truncated_salvage():
    service = ExamService.__new__(ExamService)
    # Incomplete outer JSON because of token cutoff during question 2
    raw = '{"questions": [{"id": 1, "question_text": "What is Prim\'s algorithm?", "model_answer": "Greedy MST algorithm."}, {"id": 2, "question_text": "What is Kruskal\'s'
    parsed = service._clean_and_parse_json(raw)
    assert parsed is not None
    questions = service._extract_questions(parsed)
    assert len(questions) == 1
    assert questions[0]["question_text"] == "What is Prim's algorithm?"

def test_clean_and_parse_markdown_fallback():
    service = ExamService.__new__(ExamService)
    md_text = """
    Here is the examination paper:

    Question 1: Define De Morgan's Law.
    Model Answer: De Morgan's laws relate conjunctions and disjunctions of propositions through negation.
    Rubric:
    - State theorem correctly (1 Mark)

    Question 2: Explain JK Flip-Flop.
    Model Answer: A JK flip-flop eliminates the invalid state present in SR flip-flops using feedback.
    Rubric:
    - Working truth table (1.5 Marks)
    - Circuit diagram (1.5 Marks)
    """
    parsed = service._clean_and_parse_json(md_text)
    assert parsed is not None
    questions = service._extract_questions(parsed)
    assert len(questions) == 2
    assert "De Morgan" in questions[0]["question_text"]
    assert "JK Flip-Flop" in questions[1]["question_text"]

def test_generate_fallback_questions_from_docs():
    from langchain_core.documents import Document
    service = ExamService.__new__(ExamService)
    docs = [
        Document(page_content="A multiplexer is a combinational circuit that selects binary information from one of many input lines and directs it to a single output line. The selection of a particular input line is controlled by a set of selection lines.")
    ]
    fallback_q = service._generate_fallback_questions_from_docs(docs, "DEC", 3)
    assert len(fallback_q) == 3
    assert fallback_q[0]["marks"] == 1
    assert "multiplexer" in fallback_q[0]["question_text"].lower()

