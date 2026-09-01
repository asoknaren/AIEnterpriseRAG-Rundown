# Project 1 Task Checklist: Document Processor (`01_doc_processor`)

**Project Directory**: `01_doc_processor/`  
**Purpose**: Multi-format document parsing (Docling), semantic chunking (Chonkie), and derivative artifact extraction (Ollama LLM).  
**Core Rule**: Build and run automated tests (`pytest`) at the end of every task/step to verify functionality before proceeding to the next level.

---

## 1. Environment & Project Scaffolding
- [x] Initialize `01_doc_processor/` directory structure (`src/`, `tests/`, `config/`)
- [x] Create `pyproject.toml` or `requirements.txt` with dependencies:
  - `docling`
  - `chonkie`
  - `ollama` / `httpx`
  - `pydantic>=2.0`
  - `pytest`, `pytest-asyncio`, `pytest-mock`
- [x] Create `src/config.py` with Pydantic BaseSettings (Ollama host, default model names, chunk size, overlap limits)
- [x] **Verification & Test Gate**:
  - [x] Write `tests/test_config.py` to verify settings loading and environment overrides
  - [x] Run `pytest tests/test_config.py` and ensure 100% pass before proceeding

## 2. Lineage & Envelope Data Models (`src/models/`)
- [x] Define `DocumentMetadata` model (`src/models/document.py`)
- [x] Define `Chunk` & `ArtifactType` Enum (`src/models/chunk.py`)
- [x] Define `LineageEnvelope` model (`src/models/lineage.py`) linking `doc_id`, `chunk_id`, `parent_chunk_id`, and `artifact_type`
- [x] **Verification & Test Gate**:
  - [x] Write `tests/test_models.py` to validate schema serialization, SHA256 hashing, and parent-child UUID integrity
  - [x] Run `pytest tests/test_models.py` and ensure 100% pass before proceeding

## 3. Document Parser Implementation (`src/parsers/`)
- [x] Define `BaseParser` abstract interface in `src/parsers/base.py`
- [x] Implement `DoclingParser` in `src/parsers/docling_parser.py`:
  - [x] Support PDF files (with layout analysis & OCR)
  - [x] Support DOCX / DOC files
  - [x] Support HTML files (strip boilerplate, retain content hierarchy)
  - [x] Support TXT files
  - [x] Convert parsed AST to clean Markdown representation
  - [x] Extract document metadata (title, page count, file size, SHA256 checksum)
- [x] **Verification & Test Gate**:
  - [x] Write `tests/test_parsers.py` with sample test fixtures (sample PDF, HTML, DOCX, TXT)
  - [x] Verify table, header, and metadata extraction accuracy
  - [x] Run `pytest tests/test_parsers.py` and ensure 100% pass before proceeding

## 4. Semantic Chunker Implementation (`src/chunkers/`)
- [x] Define `BaseChunker` abstract interface in `src/chunkers/base.py`
- [x] Implement `SemanticChunker` in `src/chunkers/semantic_chunker.py` using `chonkie`:
  - [x] Configure semantic sentence boundary thresholds
  - [x] Preserve heading breadcrumbs (`# Header 1 > ## Subheader 2`)
  - [x] Maintain character / token offset pointers to source Markdown
- [x] **Verification & Test Gate**:
  - [x] Write `tests/test_chunkers.py` to test boundary splitting, token boundaries, and header lineage retention
  - [x] Run `pytest tests/test_chunkers.py` and ensure 100% pass before proceeding

## 5. Derivative Artifact Generators (`src/generators/`)
- [x] Implement Ollama client wrapper with fallback model handling
- [x] Implement **Contextual Chunk Generator** (`src/generators/contextual_generator.py`):
  - [x] Prompt LLM with full document summary + chunk to generate a situational context prefix
- [x] Implement **Summary Generator** (`src/generators/summary_generator.py`):
  - [x] Generate whole-document executive summary & section-level summaries
- [x] Implement **RAPTOR 2-Tier Hierarchical Generator** (`src/generators/raptor_generator.py`):
  - [x] Group adjacent/topical semantic chunks into clusters
  - [x] Synthesize parent summary nodes linking directly to child `chunk_id`s
- [x] Implement **QA Pair Generator** (`src/generators/qa_generator.py`):
  - [x] Generate 3-5 diverse synthetic question-answer pairs per chunk
- [x] Implement **Factoid Generator** (`src/generators/factoid_generator.py`):
  - [x] Extract atomic factual statements and key named entities
- [x] **Verification & Test Gate**:
  - [x] Write `tests/test_generators.py` using mock LLM responses to test all 5 artifact generators and prompt parsing
  - [x] Run `pytest tests/test_generators.py` and ensure 100% pass before proceeding

## 6. End-to-End Processing Pipeline (`src/pipeline.py`)
- [ ] Create `DocumentProcessorPipeline` orchestration class:
  - [ ] Read input document file
  - [ ] Execute Docling parser -> Markdown
  - [ ] Execute Chonkie chunker -> Semantic Chunks
  - [ ] Trigger Ollama generators concurrently for derivative artifacts
  - [ ] Assemble standardized JSON/JSONL output payload
- [ ] **Verification & Test Gate**:
  - [ ] Write `tests/test_pipeline.py` testing complete flow from raw document to final enriched artifact envelope
  - [ ] Run `pytest tests/test_pipeline.py` and ensure 100% pass before proceeding

## 7. Project 1 Final Quality Gate
- [ ] Run full project test suite: `pytest --cov=src tests/`
- [ ] Verify test coverage >= 90%
- [ ] Verify code formatting and linting (`ruff` / `mypy`)
- [ ] Document README with usage instructions and sample output artifacts
