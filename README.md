# 🎓 AI Learning Assistant

> **An Intelligent, Grounded Retrieval-Augmented Generation (RAG) Educational Companion**

[![Version](https://img.shields.io/badge/version-v1.0-brightgreen.svg)](#-assistant-modes--future-roadmap)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg?logo=streamlit)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![Groq Llama 3.3](https://img.shields.io/badge/LLM-Groq_Llama--3.3--70B-orange.svg)](https://groq.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📖 Table of Contents
- [Overview](#-overview)
- [🎯 Assistant Modes & Future Roadmap](#-assistant-modes--future-roadmap)
- [✨ Key Features](#-key-features)
- [🏗️ System Architecture](#️-system-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📂 Directory Structure](#-directory-structure)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
- [💡 Usage](#-usage)
  - [Starting Backend API](#1-start-the-fastapi-backend)
  - [Starting Frontend UI](#2-start-the-streamlit-frontend)
- [🔌 API Endpoints](#-api-endpoints)
- [🧪 Running Tests](#-running-tests)
- [🛡️ Security & Anti-Hallucination Safeguards](#️-security--anti-hallucination-safeguards)

---

## 📘 Overview

The **AI Learning Assistant (v1.0)** is an end-to-end Retrieval-Augmented Generation (RAG) platform designed to act as an interactive study companion for students. By indexing course materials—including lecture slides, textbooks, and notes—the system delivers accurate, pedagogical explanations tailored to student queries.

Unlike generic LLM wrappers, the AI Learning Assistant uses a **two-stage retrieval pipeline** (Dense Embeddings + Cross-Encoder Reranking) combined with **strict anti-hallucination prompting** and **prompt injection defenses**. If course materials do not contain sufficient evidence, the assistant gracefully declines to answer rather than providing misleading information.

---

## 🎯 Assistant Modes & Future Roadmap

> **Current Version**: `v1.0`

The AI Learning Assistant is designed as a modular educational suite. The initial v1.0 release establishes the core RAG pipeline and **Learning Mode**, with specialized interactive learning modes planned for the upcoming **v2.0** release:

| Mode | Status | Description |
| :--- | :---: | :--- |
| 📖 **Learning Mode** | **Implemented (v1.0)** | Interactive concept exploration, deep step-by-step explanations (Definition, Intuition, Technical Explanation, Analogy, Key Takeaways), LaTeX formula rendering, and grounded document Q&A. |
| 🧩 **Quiz Mode** | *Planned (v2.0)* | AI-generated interactive quizzes, multiple-choice questions (MCQs), fill-in-the-blanks, and instant feedback tailored to your study materials to test retention. |
| 🔬 **Lab Mode** | *Planned (v2.0)* | Hands-on exercise generation, step-by-step problem-solving walkthroughs, code snippet breakdowns, and interactive analytical/coding sandbox guidance. |
| 🔄 **Revision Mode** | *Planned (v2.0)* | AI-powered flashcard generation, high-yield summary cheat sheets, formula quick-reference sheets, and rapid pre-exam refreshers. |
| 📝 **Exam Mode** | *Planned (v2.0)* | Time-bounded mock exam simulations, multi-topic comprehensive test suites, automated scoring rubrics, and detailed performance diagnostic reports. |

---

## ✨ Key Features

- 📑 **Multi-Format Document Parsing**: Seamlessly ingests and processes **PDF**, Word (**DOCX**), and PowerPoint (**PPTX**) documents while retaining page and slide metadata.
- ✂️ **Context-Aware Chunking**: Intelligently splits documents into overlapping chunks (`1000` chars, `200` overlap) preserving structural and page context.
- 🧠 **Dense Semantic Embeddings**: Utilizes HuggingFace `BAAI/bge-base-en-v1.5` embeddings for high-dimensional semantic search stored in persistent **ChromaDB**.
- 🎯 **Two-Stage Reranking**: Re-evaluates top-20 retrieved candidates using a Cross-Encoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`) to return only high-confidence (`score >= 0.35`) contexts.
- 🎓 **Pedagogical Explanation Format**: Structures explanations logically:
  1. **Definition**
  2. **Intuition**
  3. **Technical Explanation**
  4. **Example / Analogy**
  5. **Key Takeaways & LaTeX Math Formulations**
- 🛡️ **Security & Anti-Hallucination**:
  - Sanitizes user input against prompt injection attacks (e.g., system prompt extraction, rule overrides).
  - Enforces non-hallucination constraints: returns an explicit fallback when information is missing.
  - Sanitizes LLM outputs to remove internal chain-of-thought metadata.
- 💻 **Modern Dual-Layer Architecture**:
  - **FastAPI** REST Backend API with CORS, schemas, and async lifespans.
  - **Streamlit** Web UI with custom CSS, chat session state, expandable citations, and source references.

---

## 🏗️ System Architecture

```
                                  [ User Query ]
                                        │
                                        ▼
                           ┌──────────────────────────┐
                           │   Sanitization Guard     │
                           └────────────┬─────────────┘
                                        │
                                        ▼
┌─────────────────────────┐    ┌──────────────────┐    ┌────────────────────────┐
│  Multi-Format Loaders   │    │  BGE-Base v1.5   │    │   Chroma Vector DB     │
│  (PDF / DOCX / PPTX)    ├───►│ Embedding Model  ├───►│   (Dense Search K=20)  │
└─────────────────────────┘    └──────────────────┘    └───────────┬────────────┘
                                                                   │
                                                                   ▼
                                                       ┌────────────────────────┐
                                                       │ Cross-Encoder Reranker │
                                                       │  (Threshold >= 0.35)   │
                                                       └───────────┬────────────┘
                                                                   │ (Top K=5)
                                                                   ▼
┌─────────────────────────┐    ┌──────────────────┐    ┌────────────────────────┐
│ Response Sanitizer &    │◄───┤ Groq Llama 3.3   │◄───┤   Pedagogical Prompt   │
│ Source Citation Engine  │    │  70B Versatile   │    │        Builder         │
└────────────┬────────────┘    └──────────────────┘    └────────────────────────┘
             │
             ▼
┌─────────────────────────┐
│ Streamlit Frontend UI / │
│   FastAPI REST Output   │
└─────────────────────────┘
```

---

## 🛠️ Tech Stack

| Domain | Technologies Used |
| :--- | :--- |
| **LLM Inference** | [Groq Cloud API](https://groq.com/) (`llama-3.3-70b-versatile`) |
| **Embeddings** | [SentenceTransformers](https://www.sbert.net/) (`BAAI/bge-base-en-v1.5`) |
| **Reranking** | Cross-Encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) |
| **Vector Database** | [ChromaDB](https://www.trychroma.com/) Persistent Client |
| **Text Processing** | [LangChain Core](https://python.langchain.com/) Text Splitters |
| **Document Parsing**| `pypdf`, `python-docx`, `python-pptx` |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/), `uvicorn`, `pydantic` |
| **Frontend Framework**| [Streamlit](https://streamlit.io/), `requests` |
| **Testing** | `pytest` unit & integration test suite |

---

## 📂 Directory Structure

```directory
AI_Learning_Assistant/
├── app.py                      # Main entrypoint launching Streamlit frontend
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (API keys)
│
├── backend/                    # FastAPI Backend Application
│   ├── backend_app.py          # FastAPI application & lifespan loader
│   ├── routes.py               # REST API endpoints (/chat)
│   ├── schemas.py              # Pydantic request/response models
│   └── dependencies.py         # App service initialization
│
├── frontend/                   # Streamlit Frontend Application
│   ├── frontend_app.py         # Streamlit main entrypoint
│   └── ui/                     # UI components
│       ├── api_client.py       # HTTP client connecting UI to Backend API
│       ├── chat_interface.py   # Main conversational UI interface
│       ├── components.py       # Header, styling, & markdown components
│       └── sidebar.py          # Document status & navigation sidebar
│
├── core/                       # RAG Pipeline Core Modules
│   ├── chunker.py              # Text splitter & chunk generator
│   ├── embedding_model.py      # BGE embedding model wrapper
│   ├── vector_store.py         # ChromaDB persistence & similarity search
│   ├── retriever.py            # Vector retrieval logic
│   ├── reranker.py             # Cross-Encoder score & filter engine
│   ├── prompt_builder.py       # Pedagogical system & user prompt construction
│   ├── llm_client.py           # Groq API client interface
│   ├── preprocesser.py         # Text cleaning & normalization
│   ├── response_sanitizer.py   # Response formatting & cleaning
│   ├── index_manager.py        # Metadata & document index tracking
│   └── loaders/                # Custom file format loaders
│       ├── pdf_loader.py       # PDF document loader
│       ├── docx_loader.py      # DOCX Word document loader
│       └── ppt_loader.py       # PPTX presentation loader
│
├── services/                   # Business Logic & Orchestration
│   ├── app_service.py          # Master application service router
│   ├── indexing_service.py     # Document ingest & embedding pipeline service
│   └── chat_service.py         # End-to-end RAG query orchestrator
│
├── config/                     # System Settings & Prompts
│   ├── settings.py             # Configuration parameters & paths
│   └── prompts.py              # Pedagogical & guardrail prompt definitions
│
├── data/                       # Local Document Storage
│   ├── raw/                    # Directory for user uploaded PDFs/DOCX/PPTX
│   └── vector_store/           # Persistent ChromaDB storage directory
│
├── tests/                      # Unit and Integration Tests (Pytest)
└── utils/                      # Logging & utility scripts
    └── logger.py               # Structured logging utility
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** installed on your system.
- A **Groq API Key** (Get one for free at [console.groq.com](https://console.groq.com/)).

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/AdarshSU-2428/AI_Learning_assistant.git
   cd AI_Learning_assistant
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables

Create a `.env` file in the root directory of the project and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
BACKEND_API_URL=http://127.0.0.1:8000
```

---

## 💡 Usage

### 1. Place Study Documents
Drop your lecture notes, textbooks, or slides (`.pdf`, `.docx`, `.pptx`) into the `data/raw/` directory.

### 2. Start the FastAPI Backend
Launch the backend server via `uvicorn`:
```bash
uvicorn backend.backend_app:app --host 127.0.0.1 --port 8000 --reload
```
*Upon startup, the backend automatically scans `data/raw/` and indexes any new documents into ChromaDB.*

### 3. Start the Streamlit Frontend
In a separate terminal window (with virtual environment activated):
```bash
streamlit run frontend/frontend_app.py
```
Or run the top-level launcher:
```bash
python app.py
```
Open your browser at `http://localhost:8501` to start asking questions!

---

## 🧪 Running Tests

The repository includes comprehensive automated tests covering document ingestion, chunking, retrieval, reranking, and frontend/backend interactions.

Run the test suite using `pytest`:
```bash
pytest tests/
```

---

## 🛡️ Security & Anti-Hallucination Safeguards

1. **Strict Context Alignment**: The LLM is prohibited from relying on pre-trained parametric knowledge when answering domain questions.
2. **Confidence Thresholding**: If Cross-Encoder reranking scores fall below `0.35`, retrieval results are discarded, preventing noisy or irrevelant context injection.
3. **Prompt Injection Mitigation**: Regex-based sanitization patterns intercept malicious queries targeting prompt disclosure or guardrail bypasses.
4. **Clean Formatting**: Output sanitizers strip model artifacts or chain-of-thought leakage.

---

<p center>Crafted for students & educators to make learning intuitive, rigorous, and accessible.</p>
