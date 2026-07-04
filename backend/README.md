# Legal Contract Q&A Assistant — Backend

AI-powered backend service for querying legal contracts using Retrieval-Augmented Generation (RAG).

## Tech Stack

- **FastAPI** — Web framework
- **LangChain** — LLM orchestration
- **Google Gemini** — Large Language Model
- **FAISS** — Vector similarity search
- **Sentence Transformers** — Embedding generation
- **Pydantic** — Data validation

## Project Structure

```
backend/
├── app/
│   ├── api/routes/     # API endpoint definitions
│   ├── core/           # Config, logging
│   ├── models/         # Database models (future)
│   ├── schemas/        # Pydantic request/response models
│   ├── services/       # Business logic (RAG, embeddings, retrieval, LLM)
│   ├── utils/          # Helper functions
│   ├── vectorstore/    # FAISS index storage
│   ├── data/           # Uploaded documents
│   └── main.py         # FastAPI app entry point
├── tests/              # Test suite
├── requirements.txt
├── .env.example
└── run.py              # Dev server launcher
```

## Getting Started

1. **Clone the repository**
2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your GEMINI_API_KEY
   ```
5. **Run the development server**
   ```bash
   python run.py
   ```

## API Endpoints

| Method | Path          | Description          |
|--------|---------------|----------------------|
| GET    | `/health`     | Health check         |
| POST   | `/chat/ask`   | Ask a question (TBD) |

## Testing

```bash
pytest