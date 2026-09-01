"""Document and section summary generation."""

from src.models import ArtifactType, Chunk

from .ollama_client import OllamaGeneratorClient


class SummaryGenerator:
    def __init__(self, client: OllamaGeneratorClient) -> None:
        self._client = client

    def generate(self, chunk: Chunk, section: bool = False) -> Chunk:
        scope = "section" if section else "document"
        content = self._client.generate(f"Write an executive {scope} summary of:\n{chunk.content}", model=self._client.summary_model)
        return chunk.model_copy(update={"artifact_type": ArtifactType.SUMMARY, "content": content, "raw_content": chunk.content})