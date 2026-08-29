# Project 4 Task Checklist: Interactive RAG Search UI (`04_rag_ui_search`)

**Project Directory**: `04_rag_ui_search/`  
**Purpose**: Interactive Streamlit search UI, multi-artifact filtering, grounded citation viewer, and configurable RAG generation (Ollama / OpenAI).  
**Core Rule**: Build and run automated tests (`pytest`) at the end of every task/step to verify functionality before proceeding to the next level.

---

## 1. Environment & Project Scaffolding
- [ ] Initialize `04_rag_ui_search/` directory structure (`src/`, `tests/`, `assets/`)
- [ ] Create `pyproject.toml` or `requirements.txt` with dependencies:
  - `streamlit>=1.32.0`
  - `httpx>=0.25.0`
  - `ollama`
  - `openai>=1.0.0`
  - `pydantic>=2.0`
  - `pytest`, `pytest-mock`
- [ ] Create `src/config.py` with Pydantic BaseSettings (FastAPI endpoint URL, default generation provider, default models)
- [ ] **Verification & Test Gate**:
  - [ ] Write `tests/test_config.py` to test environment parsing and validation
  - [ ] Run `pytest tests/test_config.py` and ensure 100% pass before proceeding

## 2. API Client Adapter (`src/api_client.py`)
- [ ] Implement `VectorServiceClient`:
  - [ ] Execute vector search via `POST /api/v1/search`
  - [ ] Retrieve document details via `GET /api/v1/documents/{doc_id}`
  - [ ] Check service health via `GET /api/v1/health`
  - [ ] Handle backend connection failures gracefully with user-friendly error alerts
- [ ] **Verification & Test Gate**:
  - [ ] Write `tests/test_api_client.py` mocking FastAPI responses to test search query generation, payload handling, and timeout alerts
  - [ ] Run `pytest tests/test_api_client.py` and ensure 100% pass before proceeding

## 3. RAG Generation Engine (`src/rag_engine.py`)
- [ ] Implement abstract generator interface
- [ ] Implement **Ollama Generator** (Local on-premise: Llama 3.1, Gemma 2, Qwen 2.5)
- [ ] Implement **OpenAI Generator** (API-based: GPT-4o / GPT-4o-mini)
- [ ] Implement RAG prompt builder:
  - [ ] Inject retrieved context chunks with bracketed citation IDs (`[1]`, `[2]`)
  - [ ] Enforce strict anti-hallucination system instructions
  - [ ] Ground answers strictly in provided context
- [ ] **Verification & Test Gate**:
  - [ ] Write `tests/test_rag_engine.py` and `tests/test_citations.py` to test prompt formatting, citation injection, and mocked LLM outputs
  - [ ] Run `pytest tests/test_rag_engine.py tests/test_citations.py` and ensure 100% pass before proceeding

## 4. Streamlit UI Components (`src/components/`)
- [ ] Implement **Search Bar & Controls** (`src/components/search_bar.py`):
  - [ ] Query input box
  - [ ] Top-K slider & similarity score threshold slider
  - [ ] Artifact type multi-select filter (`All`, `raw_chunk`, `contextual_chunk`, `raptor_summary`, `qa_pair`, `factoid`)
  - [ ] LLM provider and model selector (Ollama vs OpenAI)
- [ ] Implement **Result Card & Citations** (`src/components/result_card.py`):
  - [ ] Display synthesized answer with interactive citation popovers
  - [ ] Display retrieved chunks, similarity scores, and document titles
- [ ] Implement **Lineage & Document Inspector** (`src/components/lineage_viewer.py`):
  - [ ] View parent RAPTOR summary nodes linked to child leaf chunks
  - [ ] Display document metadata (file source, SHA256, page numbers)
- [ ] **Verification & Test Gate**:
  - [ ] Write `tests/test_components.py` testing data formatting, score threshold filters, and tree structure rendering
  - [ ] Run `pytest tests/test_components.py` and ensure 100% pass before proceeding

## 5. Main Streamlit Application (`src/app.py`)
- [ ] Assemble full Streamlit application flow
- [ ] Implement session state management for search history and conversation state
- [ ] Add side panel for system health and connection configuration
- [ ] Optimize page load performance and error boundaries
- [ ] **Verification & Test Gate**:
  - [ ] Write `tests/test_app_integration.py` to test app state initialization and full query execution loop
  - [ ] Run `pytest tests/` and ensure 100% pass before proceeding

## 6. Project 4 Final Quality Gate
- [ ] Run full project test suite: `pytest --cov=src tests/`
- [ ] Verify test coverage >= 85%
- [ ] Verify code formatting and linting (`ruff` / `mypy`)
- [ ] Document README with `streamlit run src/app.py` instructions and screenshot walkthrough
