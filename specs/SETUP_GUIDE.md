# Local Development Machine Setup Guide: Enterprise Modular RAG Platform

## 1. Overview & Objectives

This runbook provides complete, step-by-step instructions for configuring and provisioning a local developer machine (macOS, Linux, or WSL2 on Windows) to build, run, test, and debug all four components of the Enterprise Modular RAG Platform.

---

## 2. System Prerequisites & Tools

Ensure the following tools and runtimes are installed on your workstation:

### 2.1 Core Runtime & Package Managers
| Tool | Recommended Version | Verification Command | Installation Link / Notes |
| :--- | :--- | :--- | :--- |
| **Python** | 3.11 or 3.12 | `python3 --version` | [python.org](https://www.python.org/) or via `brew install python@3.11` / `pyenv` |
| **Git** | 2.40+ | `git --version` | `brew install git` or `apt install git` |
| **Docker** | 24.0+ | `docker --version` | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **Docker Compose** | 2.20+ | `docker compose version` | Bundled with Docker Desktop |
| **Ollama** | 0.3.0+ | `ollama --version` | [ollama.ai](https://ollama.ai) (macOS: `brew install ollama`) |
| **uv** *(Optional / Fast)* | Latest | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

---

## 3. Infrastructure Setup (Databases & Vector Engines)

A centralized `docker-compose.yml` is used to run the persistence layer for local development:
- **PostgreSQL 16 with `pgvector`** (Port `5432`)
- **Qdrant Vector Database** (HTTP Port `6333`, gRPC Port `6334`)

### 3.1 Docker Compose Specification (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: rag_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ragdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgrespassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d ragdb"]
      interval: 5s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    container_name: rag_qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:6333/readyz || exit 1"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  qdrant_data:
```

### 3.2 Starting Infrastructure
```bash
# Start PostgreSQL & Qdrant in the background
docker compose up -d

# Verify both containers are healthy
docker compose ps
```

---

## 4. Local Ollama LLM & Embedding Models Setup

The platform uses on-premise models running through Ollama for document parsing enhancements, derivative artifact synthesis, and embeddings.

### 4.1 Start Ollama Service
```bash
# On macOS / Linux:
ollama serve &
```

### 4.2 Pull Required Models
Run the following commands in your terminal to download the recommended on-premise models:

```bash
# 1. Embedding Model (768-dimensional)
ollama pull nomic-embed-text

# 2. Derivative Artifact Generators & Synthesis LLMs
ollama pull llama3.2       # Recommended lightweight general reasoning
ollama pull qwen2.5:7b     # High accuracy for structured QA pairs & Factoids
ollama pull gemma2:2b      # Ultra-fast lightweight summarization
```

### 4.3 Verify Ollama Setup
```bash
# Verify models are listed
ollama list

# Test embedding generation
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "Testing local embedding generation"
}'
```

---

## 5. Master Environment Configuration (`.env`)

Create a master `.env` file in the workspace root or project directories:

```env
# ==============================================================================
# Database & Vector Store Configuration
# ==============================================================================
VECTOR_DB_BACKEND=postgres                    # 'postgres' or 'qdrant'

# PostgreSQL (asyncpg + pgvector) Settings (Strictly NO SQLAlchemy)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ragdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgrespassword
POSTGRES_MIN_CONNECTIONS=5
POSTGRES_MAX_CONNECTIONS=20

# Qdrant Settings
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=enterprise_docs_chunks

# ==============================================================================
# Embedding Engine Configuration
# ==============================================================================
EMBEDDING_PROVIDER=ollama                     # 'ollama', 'fastembed', or 'openai'
EMBEDDING_MODEL=nomic-embed-text              # e.g., 'nomic-embed-text' or 'text-embedding-3-small'
EMBEDDING_DIMENSION=768                       # 768 for nomic-embed-text, 1536 for OpenAI small

# ==============================================================================
# Ollama Local LLM Configuration
# ==============================================================================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_GENERATION_MODEL=llama3.2
OLLAMA_SUMMARY_MODEL=llama3.2
OLLAMA_QA_MODEL=qwen2.5:7b

# ==============================================================================
# External API Keys (Optional if using Ollama exclusively)
# ==============================================================================
OPENAI_API_KEY=

# ==============================================================================
# Service Endpoints
# ==============================================================================
FASTAPI_BASE_URL=http://localhost:8000
FASTAPI_PORT=8000
STREAMLIT_PORT=8501
```

---

## 6. Multi-Project Virtual Environment Setup

Each project is designed to run in isolation with its own dedicated virtual environment or under a shared workspace `uv` virtual environment.

### Option A: Using `uv` (Recommended for Speed)
```bash
# Create a single root virtual environment
uv venv .venv --python 3.11
source .venv/bin/activate

# Install all sub-projects in editable mode with development/test dependencies
uv pip install -e ./01_doc_processor
uv pip install -e ./02_ingestion_loader
uv pip install -e ./03_vector_api_service
uv pip install -e ./04_rag_ui_search
uv pip install pytest pytest-asyncio pytest-mock pytest-cov respx ruff
```

### Option B: Using Standard Python `venv`
```bash
# 1. Project 1 (Document Processor)
cd 01_doc_processor
python3.11 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
cd ..

# 2. Project 2 (Ingestion Loader)
cd 02_ingestion_loader
python3.11 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
cd ..

# 3. Project 3 (Vector API Service)
cd 03_vector_api_service
python3.11 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
cd ..

# 4. Project 4 (RAG UI Search)
cd 04_rag_ui_search
python3.11 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
cd ..
```

---

## 7. Step-by-Step Developer Runbook

### Step 1: Start Infrastructure & LLM
```bash
# 1. Start Vector DBs
docker compose up -d

# 2. Ensure Ollama is running
ollama list
```

### Step 2: Start Project 3 (FastAPI Vector Service)
```bash
cd 03_vector_api_service
source .venv/bin/activate  # or root .venv
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Verify API is healthy
curl http://localhost:8000/api/v1/health
# Response: {"status":"healthy","database":"postgres","pool_active":true}
```

### Step 3: Process Documents via Project 1 (`01_doc_processor`)
```bash
cd 01_doc_processor
source .venv/bin/activate

# Parse a sample document and generate multi-representation artifacts
python -m src.pipeline \
  --input ../sample_docs/quarterly_report.pdf \
  --output ../output/quarterly_report_artifacts.jsonl

# Inspect generated lineage & artifacts
head -n 2 ../output/quarterly_report_artifacts.jsonl
```

### Step 4: Ingest Artifacts via Project 2 (`02_ingestion_loader`)
```bash
cd 02_ingestion_loader
source .venv/bin/activate

# Ingest output artifacts into FastAPI vector storage with progress tracking
python -m src.cli ingest-file ../output/quarterly_report_artifacts.jsonl --batch-size 50
```

### Step 5: Launch Project 4 (Streamlit Interactive RAG UI)
```bash
cd 04_rag_ui_search
source .venv/bin/activate

# Start Streamlit web application
streamlit run src/app.py --server.port 8501

# Open in browser: http://localhost:8501
```

---

## 8. Continuous Testing & Quality Gates

Run automated tests per project before committing or progressing:

```bash
# Test Project 1
cd 01_doc_processor && pytest --cov=src tests/ -v && cd ..

# Test Project 2
cd 02_ingestion_loader && pytest --cov=src tests/ -v && cd ..

# Test Project 3 (includes strict rule verification: No SQLAlchemy)
cd 03_vector_api_service && pytest --cov=src tests/ -v && cd ..

# Test Project 4
cd 04_rag_ui_search && pytest --cov=src tests/ -v && cd ..
```

---

## 9. Troubleshooting & FAQ

### PostgreSQL `asyncpg` Connection Errors
- **Issue**: `asyncpg.exceptions.ConnectionDoesNotExistError` or `connection refused on port 5432`.
- **Solution**: Check container status with `docker compose ps`. Ensure no local PostgreSQL service is occupying port 5432 (`lsof -i :5432`).

### Missing `pgvector` Extension in PostgreSQL
- **Issue**: `type "vector" does not exist`.
- **Solution**: The Docker image `pgvector/pgvector:pg16` installs the extension. Verify by executing:
  ```bash
  docker compose exec postgres psql -U postgres -d ragdb -c "CREATE EXTENSION IF NOT EXISTS vector;"
  ```

### Ollama Model Connection Timeout
- **Issue**: `HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded`.
- **Solution**: Start Ollama with `ollama serve` and check if models are present via `ollama list`.
