"""End-to-end tests for the document processing pipeline."""

import json
from pathlib import Path
from uuid import uuid4

from src.models import ArtifactType, Chunk, DocumentMetadata
from src.parsers import ParsedDocument
from src.pipeline import DocumentProcessorPipeline


class FakeParser:
    def parse(self, source_path: str | Path) -> ParsedDocument:
        return ParsedDocument(
            markdown="# Report\n\nRevenue increased.",
            metadata=DocumentMetadata(title="report", source_type="txt", sha256_hash="a" * 64),
        )


class FakeChunker:
    def chunk(self, markdown, doc_id):
        return [Chunk(doc_id=doc_id, content="Revenue increased.")]


class FakeSummaryGenerator:
    def generate(self, chunk):
        return chunk.model_copy(update={"artifact_type": ArtifactType.SUMMARY, "content": "Revenue summary"})


class FakeRaptorGenerator:
    def generate(self, chunks):
        parent = Chunk(doc_id=chunks[0].doc_id, artifact_type=ArtifactType.RAPTOR_SUMMARY, content="Parent summary")
        return [parent], [chunk.model_copy(update={"parent_chunk_id": parent.chunk_id}) for chunk in chunks]


class FakeContextualGenerator:
    def generate(self, summary, chunk):
        return chunk.model_copy(update={"artifact_type": ArtifactType.CONTEXTUAL_CHUNK, "content": f"{summary}: {chunk.content}"})


class FakeQAGenerator:
    def generate(self, chunk):
        return [Chunk(doc_id=chunk.doc_id, parent_chunk_id=chunk.chunk_id, artifact_type=ArtifactType.QA_PAIR, content="Question: What?\nAnswer: Revenue")]


class FakeFactoidGenerator:
    def generate(self, chunk):
        return [Chunk(doc_id=chunk.doc_id, parent_chunk_id=chunk.chunk_id, artifact_type=ArtifactType.FACTOID, content="Revenue increased.")]


def test_pipeline_processes_document_and_writes_lineage_jsonl(tmp_path):
    """The full flow emits source-linked artifacts and valid JSONL output."""
    pipeline = DocumentProcessorPipeline(
        parser=FakeParser(), chunker=FakeChunker(), summary_generator=FakeSummaryGenerator(),
        contextual_generator=FakeContextualGenerator(), raptor_generator=FakeRaptorGenerator(),
        qa_generator=FakeQAGenerator(), factoid_generator=FakeFactoidGenerator(),
    )
    output = tmp_path / "artifacts.jsonl"

    envelopes = pipeline.process_to_jsonl("report.txt", output)

    assert {envelope.artifact_type for envelope in envelopes} == {
        ArtifactType.SUMMARY, ArtifactType.RAW_CHUNK, ArtifactType.RAPTOR_SUMMARY,
        ArtifactType.CONTEXTUAL_CHUNK, ArtifactType.QA_PAIR, ArtifactType.FACTOID,
    }
    raw_chunk = next(item for item in envelopes if item.artifact_type is ArtifactType.RAW_CHUNK)
    raptor_parent = next(item for item in envelopes if item.artifact_type is ArtifactType.RAPTOR_SUMMARY)
    assert raw_chunk.parent_chunk_id == raptor_parent.chunk_id
    assert all(item.doc_id == raw_chunk.doc_id for item in envelopes)
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(envelopes)
    assert all(json.loads(line)["doc_sha256"] == "a" * 64 for line in lines)