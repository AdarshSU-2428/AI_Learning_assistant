# 🎓 AI Learning Assistant (v1.0)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-FF6F61?style=flat)](https://www.trychroma.com/)
[![Groq Cloud](https://img.shields.io/badge/Groq-High_Speed_Inference-f05023?style=flat)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An autonomous, syllabus-grounded engineering learning platform built with an advanced Retrieval-Augmented Generation (RAG) architecture. Designed for university engineering students to master complex coursework, practice interactive quizzes, verify lab experiments and code, and simulate full-length university examinations with automated AI semantic grading.

---

## 🎯 The 4 Core Assistant Modes

The platform features **4 fully implemented, syllabus-grounded study modes** accessible through an interactive Mode Hub and sidebars:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AI Learning Assistant Hub                       │
└──────┬──────────────────┬──────────────────┬──────────────────┬────────┘
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Mode 1:     │   │  Mode 2:     │   │  Mode 3:     │   │  Mode 4:     │
│  Learning    │   │  Quiz        │   │  Lab         │   │  Exam Hall   │
│  Mode        │   │  Mode        │   │  Mode        │   │  Simulator   │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

### 📖 Mode 1: Learning Mode (Interactive Pedagogical Tutor)
- **Concept Deep-Dive**: Ask queries in any subject and receive structured, pedagogically sound explanations based strictly on uploaded textbooks and lecture slides.
- **5-Tier Pedagogical Structure**:
  1. **Definition**: Crisp, authoritative academic definition.
  2. **Intuition**: Conceptual foundation explaining *why* it works.
  3. **Technical Explanation**: Comprehensive architectural or algorithmic breakdown.
  4. **Example / Analogy**: Relatable real-world analogies and step-by-step numeric traces.
  5. **Key Takeaways & Formulae**: High-yield exam notes and standard LaTeX formulations.
- **Source Citations**: Every explanation displays clickable source citations with exact document filenames and page/slide numbers.
- **LaTeX Math Support**: Complete support for inline math (`$...$`) and block equations (`$$...$$`).

---

### 🎯 Mode 2: Quiz Mode (Interactive MCQ Studio)
- **Configurable Assessments**: Select your subject and generate from 3 to 30 multiple-choice questions tailored to **Easy**, **Medium**, or **Hard** difficulty levels.
- **Diverse Question Banks**: Leverages both pre-indexed syllabus questions (1,780+ chunks) and dynamic on-the-fly LLM generation.
- **Real-Time Interactive Feedback**:
  - Live option selection and instant score calculation.
  - Option-wise reasoning explaining why the correct answer is right and why distractors are incorrect.
  - On-demand **Hints** for guided self-study without spoiling answers.
- **Multi-Stage Truncation Resilience**: Auto-repairs formatting issues and salvages question objects under strict token constraints.

---

### 🧪 Mode 3: Lab Mode (Practical Experiments & Code Companion)
- **Universal Engineering Lab Coverage**: Supports Programming Labs (Python, C, C++, Java, Shell, SQL), Digital Electronics (DEC), Computer Organization (COA), Operating Systems (OS), and Web Technologies (IWT).
- **Runnable Working Code**: Produces modular, commented code implementations complete with sample inputs/outputs, edge case handlers, and time ($O$) / space complexity analysis.
- **Hardware & Circuits**: Provides IC component specifications, truth tables, timing diagrams, pinout guides, and circuit wiring instructions.
- **Observation Table & Error Checking**: Verifies student observation data and automatically calculates percentage error:
  $$\% \text{ Error} = \frac{|\text{Experimental} - \text{Theoretical}|}{\text{Theoretical}} \times 100\%$$
- **Oral Viva Voce Prep**: Generates high-yield viva questions with concise model answers to prepare students for practical evaluations.

---

### 📝 Mode 4: Exam Hall Simulator (Standardized University Assessment)
- **Authentic University Question Papers**: Synthesizes written examination papers from Previous Year Questions (PYQs) and syllabus course notes across all 12 subjects.
- **Standardized University Mark Weightage**:
  - **Section A (1-Mark)**: Short definitions, direct concept checks, single formulas.
  - **Section B (3-Marks)**: Analytical questions, algorithmic traces, key differences, moderate derivations.
  - **Section C (5-Marks)**: Comprehensive multi-part questions, proofs, complete code algorithms, and architectural trade-offs.
- **Written Attempt Locking**: Clean exam hall conditions where students write and save answers without premature solution reveals.
- **End-of-Exam AI Batch Evaluation**:
  - Semantically evaluates student answers against verified ground-truth model answers and multi-item rubric checklists.
  - Assigns partial credit and produces detailed question-wise deduction analysis.
- **7-Tier Official University Scorecard**:
  - Computes percentage and awards official university letter grades:
    - **O** (Outstanding: $\ge 90\%$)
    - **E** (Excellent: $80\% - 89\%$)
    - **A** (Very Good: $70\% - 79\%$)
    - **B** (Good: $60\% - 69\%$)
    - **C** (Fair: $50\% - 59\%$)
    - **D** (Pass: $40\% - 49\%$)
    - **U** (Re-appear: $< 40\%$)
- **6-Stage Resilient Parser & Syllabus Fallback**:
  - Auto-repairs unescaped LaTeX backslashes ($\Theta, \Omega, \sum, \frac{a}{b}, O(n \log n)$).
  - Salvages truncated questions and parses markdown formatted papers.
  - Automatically synthesizes syllabus-grounded questions directly from course notes if LLM rate limits occur.

---

## 📚 Supported Course Subjects

The assistant is pre-configured and indexed for 12 core university engineering courses:

| Category | Subjects |
| :--- | :--- |
| **Core Computer Science** | • Design and Analysis of Algorithms (DAA)<br>• Database Management Systems (DBMS)<br>• Operating Systems (OS)<br>• Computer Organization & Architecture (COA) |
| **Programming & Software** | • Object-Oriented Programming with Java (OOP Java)<br>• Python Programming<br>• Internet & Web Technologies (IWT) |
| **Hardware & Electronics** | • Digital Electronics and Circuits (DEC) |
| **Mathematics & AI** | • Artificial Intelligence (AI)<br>• Discrete Mathematics<br>• Optimization Techniques |
| **Interdisciplinary** | • Management and Economics for Engineering (MEE)<br>• Biology for Engineers |

---

## 🏗️ System Architecture

```
                                  [ User Query ]
                                         │
                                         ▼
                            ┌──────────────────────────┐
                            │   Safety & Input Guard   │
                            └────────────┬─────────────┘
                                         │
                                         ▼
 ┌─────────────────────────┐    ┌──────────────────┐    ┌─────────────────────────┐
 │ Multi-Format Extractors │    │ BGE-Base v1.5    │    │ ChromaDB Vector Storage │
 │ (PDF / DOCX / PPTX)     ├───►│ Dense Embedding  ├───►│ • learning_assistant    │
 └─────────────────────────┘    │ Model            │    │ • exam_paper            │
                                └──────────────────┘    │ • quiz_bank             │
                                                        │ • lab_manual            │
                                                        └───────────┬─────────────┘
                                                                    │ (Top 20-30 chunks)
                                                                    ▼
                                                        ┌─────────────────────────┐
                                                        │ Cross-Encoder Reranker  │
                                                        │ (ms-marco-MiniLM-L-6)   │
                                                        └───────────┬─────────────┘
                                                                    │ (Top K=5-12)
                                                                    ▼
 ┌─────────────────────────┐    ┌──────────────────┐    ┌─────────────────────────┐
 │ Cleaned Structured UI / │◄───┤ Groq LLM Client  │◄───┤ Dynamic Context &       │
 │ 7-Tier University Grade │    │ (Fallback Array) │    │ Prompt Builder          │
 └─────────────────────────┘    └──────────────────┘    └─────────────────────────┘
```

---

## 🛠️ Technology Stack

| Domain | Technologies Used |
| :--- | :--- |
| **LLM Inference** | [Groq Cloud](https://groq.com/) (`qwen/qwen3.8-27b`, `openai/gpt-oss-120b`, `openai/gpt-oss-20b`) |
| **Dense Embeddings** | [SentenceTransformers](https://www.sbert.net/) (`BAAI/bge-base-en-v1.5`, 768-dim) |
| **Reranking Engine** | Cross-Encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) |
| **Vector Database** | [ChromaDB](https://www.trychroma.com/) Persistent Client (7,600+ indexed chunks) |
| **Document Processing**| `pypdf`, `python-docx`, `python-pptx`, `PyMuPDF` |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/), `uvicorn`, `pydantic` |
| **Web Frontend** | [Streamlit](https://streamlit.io/) with custom dark-mode CSS and component isolation |
| **Test Suite** | `pytest` with unit tests for RAG pipeline, parsing, and grading |

---

## 📂 Project Structure

```directory
AI_Learning_Assistant/
├── app.py                      # Top-level application launcher
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (GROQ_API_KEY)
│
├── backend/                    # FastAPI Backend Server
│   ├── backend_app.py          # App initialization & lifespan
│   ├── routes.py               # Endpoints: /chat, /quiz, /lab, /exam
│   ├── schemas.py              # Pydantic request & response models
│   └── dependencies.py         # Shared service injection
│
├── frontend/                   # Streamlit Frontend Client
│   ├── frontend_app.py         # Main multi-mode controller & router
│   └── ui/                     # UI modules & components
│       ├── api_client.py       # REST client for backend communication
│       ├── components.py       # Reusable UI cards, banners, scorecards
│       ├── sidebar.py          # Unified sidebar for all 4 modes
│       ├── learning_interface.py # Mode 1: Learning Mode view
│       ├── quiz_interface.py   # Mode 2: Quiz Mode view
│       ├── lab_interface.py    # Mode 3: Lab Mode view
│       └── exam_interface.py   # Mode 4: Exam Hall Simulator view
│
├── core/                       # Core Retrieval & NLP Engine
│   ├── embedding_model.py      # BAAI/bge-base-en-v1.5 wrapper
│   ├── vector_store.py         # ChromaDB persistence & filtering
│   ├── retriever.py            # Subject & content-type retriever
│   ├── reranker.py             # Cross-encoder candidate scorer
│   ├── relevance_gate.py       # Syllabus threshold & OCR resilience gate
│   ├── prompt_builder.py       # Pedagogical & rubric prompt builder
│   ├── llm_client.py           # Multi-model Groq API client with auto-fallback
│   ├── chunker.py              # Recursive text chunker (1000/200 overlap)
│   ├── loader.py               # PDF, DOCX, PPTX document loader
│   ├── ocr_engine.py           # Tesseract OCR for handwritten notes
│   └── safety_manager.py       # Prompt injection sanitization
│
├── services/                   # Business Logic & Orchestration
│   ├── app_service.py          # Central coordinator
│   ├── learning_service.py     # Learning Mode orchestration
│   ├── quiz_service.py         # Quiz generation & scoring
│   ├── lab_service.py          # Practical experiment assistance
│   └── exam_service.py         # Exam generation, parsing, & grading
│
├── config/                     # Settings & Prompts
│   ├── settings.py             # Global constants, paths, thresholds
│   └── prompts.py              # System prompts for all 4 modes
│
├── data/                       # Local Data & Indices
│   ├── raw/                    # Uploaded PDFs, course notes, PYQs
│   └── vector_store/           # Persistent ChromaDB collections
│
└── tests/                      # Automated Test Suite (Pytest)
    ├── test_exam_parsing.py    # Multi-stage JSON parser & fallback tests
    ├── test_exam_service.py    # Exam generation & grading tests
    ├── test_quiz_service.py    # Quiz generation & scoring tests
    ├── test_lab_service.py     # Lab mode verification tests
    └── ...                     # Comprehensive unit & integration tests
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+**
- A free **Groq Cloud API Key** from [console.groq.com](https://console.groq.com/)

### 2. Installation
```powershell
# Clone the repository
git clone https://github.com/AdarshSU-2428/AI_Learning_assistant.git
cd AI_Learning_assistant

# Create and activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 4. Running the Application

Open two terminal windows:

**Terminal 1 — Launch Backend API**:
```powershell
python -m uvicorn backend.backend_app:app --port 8000 --reload
```

**Terminal 2 — Launch Frontend Interface**:
```powershell
streamlit run app.py
```

Open your browser at **`http://localhost:8501`** to access the AI Learning Assistant!

---

## 🧪 Testing

Run the automated test suite with pytest:
```powershell
# Run all tests
pytest

# Test the Exam Mode resilient parser and syllabus fallbacks
pytest tests/test_exam_parsing.py -v
```

---

<p align="center">
  <b>AI Learning Assistant v1.0</b> • Built with precision for engineering excellence.
</p>
