"""Contextual chunk generation."""

from src.models import ArtifactType, Chunk

from .ollama_client import OllamaGeneratorClient


class ContextualChunkGenerator:
    def __init__(self, client: OllamaGeneratorClient) -> None:
        self._client = client

    def generate(self, document_summary: str, chunk: Chunk) -> Chunk:
        context = self._client.generate(f"Document summary:\n{document_summary}\n\nChunk:\n{chunk.content}\n\nWrite a concise situational context prefix.")
        return chunk.model_copy(update={"artifact_type": ArtifactType.CONTEXTUAL_CHUNK, "content": f"{context}\n\n{chunk.content}", "raw_content": chunk.content})