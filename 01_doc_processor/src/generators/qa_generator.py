"""Synthetic question-answer pair generation."""

import json

from src.models import ArtifactType, Chunk

from .ollama_client import OllamaGeneratorClient


class QAPairGenerator:
    def __init__(self, client: OllamaGeneratorClient) -> None:
        self._client = client

    def generate(self, chunk: Chunk) -> list[Chunk]:
        pairs = json.loads(self._client.generate("Return 3 to 5 diverse question-answer objects with question and answer fields for:\n" + chunk.content, model=self._client.qa_model, json_mode=True))
        if not 3 <= len(pairs) <= 5:
            raise ValueError("Ollama must return between 3 and 5 QA pairs")
        return [Chunk(doc_id=chunk.doc_id, parent_chunk_id=chunk.chunk_id, artifact_type=ArtifactType.QA_PAIR, content=f"Question: {pair['question']}\nAnswer: {pair['answer']}", raw_content=chunk.content) for pair in pairs]