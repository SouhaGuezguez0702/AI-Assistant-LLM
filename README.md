# 🩺 Healthcare AI Assistant

An AI-powered healthcare assistant built with **Large Language Models (LLMs)** and **Retrieval-Augmented Generation (RAG)** to explore how relevant medical information can be retrieved from trusted documents and used to generate context-aware responses.

## 📌 Project Overview

The Healthcare AI Assistant is designed to make healthcare information more accessible through a conversational interface. It combines a language model with document retrieval, allowing the system to use relevant passages from a medical knowledge source when answering users' questions.

The project explores the integration of Generative AI, semantic search, and backend API development in a healthcare information setting.

## 🎯 Objectives

- Explore the practical application of Large Language Models in healthcare information access.
- Implement a Retrieval-Augmented Generation (RAG) pipeline to retrieve relevant document passages.
- Connect a language model to retrieved contextual information.
- Develop a backend API for processing user messages.
- Build an interactive conversational interface.
- Explore the limitations and responsible use of AI-generated healthcare information.

## 🛠️ Technologies

| Technology | Purpose |
|---|---|
| Python | Main development language |
| Mistral 7B | Language model for response generation |
| Ollama | Local LLM execution |
| LangChain | RAG pipeline integration |
| Hugging Face Embeddings | Text representation for semantic retrieval |
| ChromaDB | Vector storage and similarity search |
| FastAPI | Backend API |
| Streamlit | Interactive chat interface |

## 🏗️ Architecture

The application follows a document-grounded question-answering workflow:

1. **Document ingestion:** Load the available medical document.
2. **Text processing:** Split the document into smaller chunks.
3. **Embedding generation:** Convert text chunks into vector representations.
4. **Vector storage:** Store embeddings in ChromaDB.
5. **Semantic retrieval:** Retrieve passages relevant to the user's question.
6. **Response generation:** Provide the question and retrieved context to the Mistral language model.
7. **User interaction:** Display the response through the Streamlit interface, with FastAPI handling backend requests.

### Workflow

`Medical Documents → Text Chunking → Embeddings → ChromaDB → Relevant Context → Mistral LLM → Response`

## 📂 Project Structure

```text
AI_Assistant_Project/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── chat.py
│   │   ├── core/
│   │   ├── models/
│   │   │   └── chat_models.py
│   │   ├── services/
│   │   │   ├── chat_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── auth_service.py
│   │   │   └── conversation_service.py
│   │   └── main.py
│   ├── test_rag.py
│   └── test_rag_mistral.py
├── data/
│   └── documents/
├── frontend/
│   └── app.py
├── .gitignore
├── README.md
└── requirements.txt
```

*The structure above reflects the intended organization; adjust filenames to match the actual files in your repository.*

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version supported by the installed dependencies
- [Ollama](https://ollama.com/)
- Git

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AI_Assistant_Project
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

If `requirements.txt` has not been created yet, generate it from the project's activated environment after checking that it contains the dependencies needed to run the application.

### 4. Download the language model

```powershell
ollama pull mistral
```

Make sure Ollama is running before starting the application.

### 5. Start the backend

From the project root, open a terminal and run:

```powershell
uvicorn backend.app.main:app --reload
```

The FastAPI API should be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 6. Start the frontend

Open a second terminal, activate the virtual environment, and run:

```powershell
python -m streamlit run frontend/app.py
```

The Streamlit interface will open in your browser.

## 🧪 Testing

The project includes scripts for testing document retrieval and LLM responses.

Run the relevant test scripts from the project root according to their imports and configuration. For example:

```powershell
python -m backend.test_rag
```

## 🔒 Responsible Use

This project is an educational prototype for healthcare information retrieval and conversational AI. It is **not a medical diagnostic tool** and does not replace a qualified healthcare professional.

AI-generated responses may be incomplete or inaccurate. Medical information should be checked against reliable sources, and urgent symptoms require appropriate professional or emergency care.

## 🚀 Future Improvements

- Expand the knowledge base with appropriately licensed, reliable medical documents.
- Display retrieved sources alongside generated answers.
- Improve conversation history management.
- Add evaluation of retrieval relevance and answer quality.
- Introduce stronger safeguards for medical questions and unsupported answers.
- Improve error handling and user experience.

## 👩‍💻 Author

Developed as part of an exploration of **Generative AI, Large Language Models, and Retrieval-Augmented Generation** in healthcare information systems.