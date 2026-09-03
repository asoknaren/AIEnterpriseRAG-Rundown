# Project 2 Task Checklist: Ingestion Loader (`02_ingestion_loader`)

**Project Directory**: `02_ingestion_loader/`  
**Purpose**: Batch file scanning, deduplication validation, and resilient HTTP dispatching to Project 3 FastAPI endpoints.  
**Core Rule**: Build and run automated tests (`pytest`) at the end of every task/step to verify functionality before proceeding to the next level.

---

## 1. Environment & Project Scaffolding
- [x] Initialize `02_ingestion_loader/` directory structure (`src/`, `tests/`)
- [x] Create `pyproject.toml` or `requirements.txt` with dependencies:
  - `httpx>=0.25.0`
  - `typer>=0.9.0`
  - `rich>=13.0.0`
  - `pydantic>=2.0`
  - `pytest`, `pytest-asyncio`, `respx` / `pytest-httpx`
- [x] Create `src/config.py` with Pydantic BaseSettings (Target API base URL, batch size, timeout, max retries)
- [x] **Verification & Test Gate**:
  - [x] Write `tests/test_config.py` to verify configuration settings, URL validation, and environment loading
  - [x] Run `pytest tests/test_config.py` and ensure 100% pass before proceeding

## 2. API Client Implementation (`src/client/`)
- [ ] Implement `VectorApiClient` in `src/client/api_client.py`:
  - [ ] Async HTTP methods via `httpx.AsyncClient`
  - [ ] `check_document_exists(sha256_hash: str)` -> `bool`
  - [ ] `register_document(doc_payload: dict)` -> `dict`
  - [ ] `ingest_chunk_batch(chunks_payload: list)` -> `dict`
  - [ ] Implement exponential backoff and retry policy for HTTP 429 and 5xx errors
  - [ ] Implement network timeout and connection error handlers
- [ ] **Verification & Test Gate**:
  - [ ] Write `tests/test_client.py` and `tests/test_client_retries.py` using `respx` to test successful calls, retries, 429 backoff, and error reporting
  - [ ] Run `pytest tests/test_client*.py` and ensure 100% pass before proceeding

## 3. Loader & Deduplication Logic (`src/loader.py`)
- [ ] Implement document scanner supporting single files and directory recursion
- [ ] Implement payload parser for Project 1 output format (JSON/JSONL)
- [ ] Implement SHA256 checksum verification:
  - [ ] Check if document already exists on server
  - [ ] Skip redundant uploads unless `--force` flag is specified
- [ ] Implement chunk batch partitioning (e.g., batches of 50 chunks per HTTP POST)
- [ ] **Verification & Test Gate**:
  - [ ] Write `tests/test_loader.py` with mock directory fixtures, duplicate checksums, and batch chunk splitting
  - [ ] Run `pytest tests/test_loader.py` and ensure 100% pass before proceeding

## 4. CLI Runner Interface (`src/cli.py`)
- [ ] Build Typer CLI application:
  - [ ] Command `ingest-file <path-to-file>`
  - [ ] Command `ingest-dir <path-to-folder>`
  - [ ] Flags: `--batch-size`, `--dry-run`, `--force`, `--concurrency`
- [ ] Integrate Rich progress bars, live status display, and execution summary tables
- [ ] **Verification & Test Gate**:
  - [ ] Write `tests/test_cli.py` using Typer's `CliRunner` to test CLI arguments, flag handling, help output, and exit codes
  - [ ] Run `pytest tests/test_cli.py` and ensure 100% pass before proceeding

## 5. Project 2 Final Quality Gate
- [ ] Run full project test suite: `pytest --cov=src tests/`
- [ ] Verify test coverage >= 90%
- [ ] Verify code formatting and linting (`ruff` / `mypy`)
- [ ] Document README with CLI commands, options, and usage examples
