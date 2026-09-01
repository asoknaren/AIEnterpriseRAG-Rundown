# Vector API Service

FastAPI service for storing document metadata and vectorized RAG artifacts in PostgreSQL with pgvector or Qdrant.

## Setup

```powershell
cd 03_vector_api_service
..\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Set configuration through environment variables. Defaults match the root `.env.example` and local Docker services.