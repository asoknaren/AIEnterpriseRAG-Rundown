"""Lightweight two-tier RAPTOR summary generation."""

from itertools import batched
from uuid import uuid4

from src.models import ArtifactType, Chunk

from .ollama_client import OllamaGeneratorClient


class RaptorGenerator:
    def __init__(self, client: OllamaGeneratorClient, cluster_size: int = 5) -> None:
        self._client = client
        self._cluster_size = cluster_size

    def generate(self, chunks: list[Chunk]) -> tuple[list[Chunk], list[Chunk]]:
        parents: list[Chunk] = []
        children: list[Chunk] = []
        for cluster in batched(chunks, self._cluster_size):
            parent = Chunk(doc_id=cluster[0].doc_id, artifact_type=ArtifactType.RAPTOR_SUMMARY, content=self._client.generate("Summarize these related chunks:\n" + "\n".join(item.content for item in cluster)), metadata={"child_chunk_ids": [str(item.chunk_id) for item in cluster]})
            parents.append(parent)
            children.extend(item.model_copy(update={"parent_chunk_id": parent.chunk_id}) for item in cluster)
        return parents, children