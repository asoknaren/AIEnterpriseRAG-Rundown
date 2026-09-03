# Vector API Service

FastAPI service for storing document metadata and vectorized RAG artifacts in PostgreSQL with pgvector or Qdrant.

## Prerequisites

- Python 3.11 or later.
- Docker Compose services started from the workspace root: PostgreSQL with pgvector and/or Qdrant.
- Ollama running for local embeddings, or `OPENAI_API_KEY` configured when using OpenAI embeddings.

## Install

```bash
cd 03_vector_api_service
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

On Windows PowerShell, activate the environment using `.venv\Scripts\Activate.ps1`.

## Configuration

Copy the workspace `.env.example` to `.env`, then set the storage and embedding providers:

```env
VECTOR_DB_BACKEND=postgres
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=
```

Supported provider/model combinations and their derived vector dimensions are:

| Provider | Model | Dimension |
| --- | --- | ---: |
| `ollama` | `nomic-embed-text` | 768 |
| `ollama` | `mxbai-embed-large` | 1024 |
| `fastembed` | `BAAI/bge-small-en-v1.5` | 384 |
| `fastembed` | `BAAI/bge-base-en-v1.5` | 768 |
| `openai` | `text-embedding-3-small` | 1536 |
| `openai` | `text-embedding-3-large` | 3072 |

The selected model determines `embedding_dimension`. PostgreSQL's `vector(n)` schema and the Qdrant collection must use that same size. Changing models after ingestion requires a database/collection migration and re-embedding existing records.

## Database Setup

From the workspace root, start local infrastructure:

```bash
docker compose up -d
docker compose ps
```

For PostgreSQL, apply [src/db/postgres/schema.sql](src/db/postgres/schema.sql) once after creating the database. It enables `pgvector`, creates document/chunk tables, and creates the HNSW vector index. The API uses direct `asyncpg` queries; SQLAlchemy is not used.

For Qdrant, set `VECTOR_DB_BACKEND=qdrant`. The collection initializer uses cosine distance and the dimension derived from the configured embedding model.

## Run

```bash
cd 03_vector_api_service
source .venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

OpenAPI documentation is available at `http://localhost:8000/docs`.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Service and selected backend health status. |
| `POST` | `/api/v1/documents` | Register one document; rejects duplicate SHA256 checksums. |
| `GET` | `/api/v1/documents/{doc_id}` | Retrieve document metadata. |
| `GET` | `/api/v1/documents/by-hash/{sha256_hash}` | Find a document by source checksum. |
| `DELETE` | `/api/v1/documents/{doc_id}` | Delete a document and its chunks. |
| `POST` | `/api/v1/chunks/batch` | Store up to 500 chunks and generate omitted embeddings. |
| `POST` | `/api/v1/search` | Embed a query and return filtered similarity results. |

## Quality Checks

```bash
python -m pytest --cov=src --cov-report=term-missing tests/ -v
python -m ruff check src tests
python -m mypy src
```