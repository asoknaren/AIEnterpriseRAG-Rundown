# Document Processor

Converts PDF, DOCX, DOC, HTML, and TXT documents into normalized Markdown, semantic chunks, and lineage-aware derivative artifacts generated through Ollama.

## Setup

```powershell
cd 01_doc_processor
..\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Run Ollama locally and pull the configured models before processing a document:

```powershell
ollama pull llama3.2
ollama pull qwen2.5:7b
```

## Process A Document

```python
from src.pipeline import DocumentProcessorPipeline

pipeline = DocumentProcessorPipeline()
artifacts = pipeline.process_to_jsonl(
    "../sample_docs/quarterly_report.pdf",
    "../output/quarterly_report_artifacts.jsonl",
)
```

Each JSONL record contains source document metadata, `chunk_id`, optional `parent_chunk_id`, `artifact_type`, content, raw content, and source offsets or heading lineage. Artifact types are `raw_chunk`, `contextual_chunk`, `summary`, `raptor_summary`, `qa_pair`, and `factoid`.

## Verify

```powershell
..\.venv\Scripts\python.exe -m pytest --cov=src tests
..\.venv\Scripts\python.exe -m ruff check src tests
..\.venv\Scripts\python.exe -m mypy src
```