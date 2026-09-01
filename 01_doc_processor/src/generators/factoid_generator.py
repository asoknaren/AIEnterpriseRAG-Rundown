"""Atomic fact and entity extraction."""

import json

from src.models import ArtifactType, Chunk

from .ollama_client import OllamaGeneratorClient


class FactoidGenerator:
    def __init__(self, client: OllamaGeneratorClient) -> None:
        self._client = client

    def generate(self, chunk: Chunk) -> list[Chunk]:
        facts = json.loads(self._client.generate("Return a JSON array of atomic factual statements and named entities from:\n" + chunk.content, json_mode=True))
        return [Chunk(doc_id=chunk.doc_id, parent_chunk_id=chunk.chunk_id, artifact_type=ArtifactType.FACTOID, content=fact, raw_content=chunk.content) for fact in facts]