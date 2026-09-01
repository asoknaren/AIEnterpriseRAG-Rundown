"""End-to-end document processing and JSONL artifact output."""

import json
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import cast

from src.chunkers import BaseChunker, SemanticChunker
from src.generators import (
    ContextualChunkGenerator,
    FactoidGenerator,
    QAPairGenerator,
    RaptorGenerator,
    SummaryGenerator,
)
from src.generators.ollama_client import OllamaGeneratorClient
from src.models import Chunk, LineageEnvelope
from src.parsers import BaseParser, DoclingParser, ParsedDocument


class DocumentProcessorPipeline:
    """Compose parsing, semantic chunking, derivative generation, and export."""

    def __init__(
        self,
        parser: BaseParser | None = None,
        chunker: BaseChunker | None = None,
        summary_generator: SummaryGenerator | None = None,
        contextual_generator: ContextualChunkGenerator | None = None,
        raptor_generator: RaptorGenerator | None = None,
        qa_generator: QAPairGenerator | None = None,
        factoid_generator: FactoidGenerator | None = None,
    ) -> None:
        client = OllamaGeneratorClient()
        self._parser = parser or DoclingParser()
        self._chunker = chunker or SemanticChunker()
        self._summary_generator = summary_generator or SummaryGenerator(client)
        self._contextual_generator = contextual_generator or ContextualChunkGenerator(client)
        self._raptor_generator = raptor_generator or RaptorGenerator(client)
        self._qa_generator = qa_generator or QAPairGenerator(client)
        self._factoid_generator = factoid_generator or FactoidGenerator(client)

    def process(self, source_path: str | Path) -> list[LineageEnvelope]:
        """Process a source document into normalized lineage envelopes."""
        parsed = self._parser.parse(source_path)
        document_chunk = Chunk(doc_id=parsed.metadata.doc_id, content=parsed.markdown)
        summary = self._summary_generator.generate(document_chunk)
        raw_chunks = self._chunker.chunk(parsed.markdown, parsed.metadata.doc_id)
        raptor_parents, leaf_chunks = self._raptor_generator.generate(raw_chunks)

        artifacts: list[Chunk] = [summary, *leaf_chunks, *raptor_parents]
        with ThreadPoolExecutor() as executor:
            futures: list[Future[Chunk | list[Chunk]]] = []
            for chunk in leaf_chunks:
                futures.extend(
                    (
                        cast(Future[Chunk | list[Chunk]], executor.submit(self._contextual_generator.generate, summary.content, chunk)),
                        cast(Future[Chunk | list[Chunk]], executor.submit(self._qa_generator.generate, chunk)),
                        cast(Future[Chunk | list[Chunk]], executor.submit(self._factoid_generator.generate, chunk)),
                    )
                )
            for future in futures:
                result = future.result()
                artifacts.extend(result if isinstance(result, list) else [result])

        return [self._to_envelope(parsed, artifact) for artifact in artifacts]

    def process_to_jsonl(self, source_path: str | Path, output_path: str | Path) -> list[LineageEnvelope]:
        """Process a document and persist one JSON envelope per output line."""
        envelopes = self.process(source_path)
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("\n".join(json.dumps(envelope.model_dump(mode="json")) for envelope in envelopes) + "\n", encoding="utf-8")
        return envelopes

    @staticmethod
    def _to_envelope(parsed: ParsedDocument, artifact: Chunk) -> LineageEnvelope:
        return LineageEnvelope(
            doc_id=parsed.metadata.doc_id,
            doc_title=parsed.metadata.title,
            doc_sha256=parsed.metadata.sha256_hash,
            doc_source_type=parsed.metadata.source_type,
            chunk_id=artifact.chunk_id,
            parent_chunk_id=artifact.parent_chunk_id,
            artifact_type=artifact.artifact_type,
            content=artifact.content,
            raw_content=artifact.raw_content,
            metadata=artifact.metadata,
        )