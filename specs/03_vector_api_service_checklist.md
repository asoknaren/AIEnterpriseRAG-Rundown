# Project 3 Task Checklist: Vector Storage & CRUD FastAPI (`03_vector_api_service`)

**Project Directory**: `03_vector_api_service/`  
**Purpose**: High-performance FastAPI vector storage, CRUD, and hybrid/vector similarity search.  
**Critical Constraint**: Strictly **NO SQLAlchemy**. Direct `asyncpg` raw SQL for PostgreSQL/pgvector or `qdrant-client` for Qdrant.  
**Core Rule**: Build and run automated tests (`pytest`) at the end of every task/step to verify functionality before proceeding to the next level.

---

## 1. Environment & Project Scaffolding
- [x] Initialize `03_vector_api_service/` directory structure (`src/`, `tests/`)
- [x] Create `pyproject.toml` or `requirements.txt` with dependencies:
  - `fastapi>=0.110.0`
  - `uvicorn[standard]>=0.28.0`
  - `asyncpg>=0.29.0` (PostgreSQL driver)
  - `pgvector>=0.2.5`
  - `qdrant-client>=1.8.0`
  - `pydantic>=2.0`
  - `pydantic-settings>=2.0`
  - `ollama` / `fastembed` / `openai`
  - `pytest`, `pytest-asyncio`, `httpx`
- [x] Create `src/config.py` with Pydantic BaseSettings:
  - Database backend toggle: `VECTOR_DB_BACKEND` (`postgres` | `qdrant`)
  - PostgreSQL connection parameters (host, port, user, password, db, pool sizes)
  - Qdrant connection parameters (URL, API key, collection name)
  - Embedding provider settings: `EMBEDDING_PROVIDER` (`ollama` | `fastembed` | `openai`)
- [x] **Verification & Test Gate**:
  - [x] Write `tests/test_config.py` to test environment parsing and validation
  - [x] Run `pytest tests/test_config.py` and ensure 100% pass before proceeding

## 2. DTOs & Validation Schemas (`src/schemas/`)
- [x] Document request/response schemas (`src/schemas/document_dto.py`)
- [x] Chunk batch request/response schemas (`src/schemas/chunk_dto.py`)
- [x] Search query request and scored result response schemas (`src/schemas/search_dto.py`)
- [x] **Verification & Test Gate**:
  - [x] Write `tests/test_schemas.py` to validate payload structures, required fields, and serialization
  - [x] Run `pytest tests/test_schemas.py` and ensure 100% pass before proceeding

## 3. Database Layer - Strictly NO SQLAlchemy (`src/db/`)
- [x] Define abstract `BaseVectorRepository` in `src/db/base.py`
- [x] Implement **PostgreSQL (`asyncpg` + `pgvector`)** repository (`src/db/postgres/`):
  - [x] Connection pool manager in `src/db/postgres/connection.py`
  - [x] Schema DDL script in `src/db/postgres/schema.sql`:
    - Enable `vector` and `uuid-ossp` extensions
    - `documents` table
    - `document_chunks` table with `vector(dim)` column
    - HNSW index on `document_chunks.embedding` using `vector_cosine_ops`
    - Foreign keys with `ON DELETE CASCADE`
  - [x] Repository queries in `src/db/postgres/repository.py` using direct `asyncpg` raw parameterized SQL:
    - `create_document()`, `get_document()`, `delete_document()`, `get_document_by_hash()`
    - `insert_chunks_batch()`, `delete_chunks_by_doc()`
    - `search_similar_chunks()` (Cosine similarity with SQL `ORDER BY embedding <=> $1 LIMIT $2`)
- [x] Implement **Qdrant** repository (`src/db/qdrant/`):
  - [x] Client connection manager in `src/db/qdrant/connection.py`
  - [x] Collection initializer with cosine distance in `src/db/qdrant/schema.py`
  - [x] Repository implementation in `src/db/qdrant/repository.py` using `AsyncQdrantClient`
- [x] Implement `RepositoryFactory` in `src/db/factory.py` to resolve backend dynamically
- [x] **Verification & Test Gate**:
  - [x] Write `tests/test_db_postgres.py` with mock/test asyncpg connection pool to test raw SQL execution and cascade logic
  - [x] Write `tests/test_db_qdrant.py` with mock Qdrant client to test collection queries and vector filters
  - [x] Write `tests/test_architecture_rules.py` asserting no imports or dependencies on `sqlalchemy` exist in `src/`
  - [x] Run `pytest tests/test_db_*.py tests/test_architecture_rules.py` and ensure 100% pass before proceeding

## 4. Embedding Engine Layer (`src/embeddings/`)
- [x] Define `BaseEmbeddingService` abstract interface in `src/embeddings/base.py`
- [x] Implement `OllamaEmbeddingService` (`src/embeddings/ollama_embed.py`)
- [x] Implement `FastEmbedService` (`src/embeddings/fastembed_embed.py`)
- [x] Implement `OpenAIEmbeddingService` (`src/embeddings/openai_embed.py`)
- [x] Implement `EmbeddingFactory` in `src/embeddings/factory.py`
- [x] **Verification & Test Gate**:
  - [x] Write `tests/test_embeddings.py` testing dimension checking, batch embedding generation, and error handling
  - [x] Run `pytest tests/test_embeddings.py` and ensure 100% pass before proceeding

## 5. FastAPI REST API Routers (`src/api/`)
- [x] Implement **Document Endpoints** (`src/api/v1/documents.py`):
  - `POST /api/v1/documents` -> Register document & metadata
  - `GET /api/v1/documents/{doc_id}` -> Retrieve document with chunks
  - `DELETE /api/v1/documents/{doc_id}` -> Cascade delete document & vectors
  - `GET /api/v1/documents/by-hash/{sha256}` -> Check existence by checksum
- [x] Implement **Chunk Ingestion Endpoints** (`src/api/v1/chunks.py`):
  - `POST /api/v1/chunks/batch` -> Compute embeddings (if not supplied) and insert chunks
- [x] Implement **Search Endpoints** (`src/api/v1/search.py`):
  - `POST /api/v1/search` -> Similarity search with filters: `artifact_type`, `doc_id`, `score_threshold`, `top_k`
- [x] Implement **Health Endpoint** (`src/api/v1/health.py`):
  - `GET /api/v1/health` -> Check API and DB connection pool status
- [x] Set up lifespan context manager for graceful startup/shutdown of DB pools in `src/main.py`
- [x] **Verification & Test Gate**:
  - [x] Write `tests/test_api_v1.py` using `httpx.AsyncClient` & `ASGITransport` to test all CRUD and search routes
  - [x] Run `pytest tests/test_api_v1.py` and ensure 100% pass before proceeding

## 6. Project 3 Final Quality Gate
- [x] Run full project test suite: `pytest --cov=src tests/`
- [x] Verify test coverage >= 90% (verified: 92%)
- [x] Verify code formatting and linting (`ruff` / `mypy`)
- [x] Document README with API specs, OpenAPI schema, and database setup instructions
