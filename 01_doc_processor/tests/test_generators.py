"""Mock-driven tests for Ollama derivative artifact generators."""

from types import SimpleNamespace
from uuid import uuid4

from src.generators import ContextualChunkGenerator, FactoidGenerator, QAPairGenerator, RaptorGenerator, SummaryGenerator
from src.generators.ollama_client import OllamaGeneratorClient
from src.models import ArtifactType, Chunk


class FakeOllama:
    def __init__(self, responses, fail_first=False):
        self.responses = iter(responses)
        self.calls = []
        self.fail_first = fail_first

    def generate(self, **kwargs):
        self.calls.append(kwargs)
        if self.fail_first and len(self.calls) == 1:
            raise ConnectionError("primary unavailable")
        return SimpleNamespace(response=next(self.responses))


def client_with(*responses):
    fake = FakeOllama(responses)
    return OllamaGeneratorClient(client_factory=lambda **kwargs: fake), fake


def test_client_retries_fallback_model():
    fake = FakeOllama(["fallback response"], fail_first=True)
    client = OllamaGeneratorClient(client_factory=lambda **kwargs: fake)
    assert client.generate("prompt", model="primary", fallback_model="fallback") == "fallback response"
    assert [call["model"] for call in fake.calls] == ["primary", "fallback"]


def test_contextual_and_summary_generators_build_typed_artifacts():
    client, fake = client_with("Context", "Executive overview")
    chunk = Chunk(doc_id=uuid4(), content="Revenue rose.")
    contextual = ContextualChunkGenerator(client).generate("Quarterly report", chunk)
    summary = SummaryGenerator(client).generate(chunk)
    assert contextual.artifact_type is ArtifactType.CONTEXTUAL_CHUNK
    assert contextual.content == "Context\n\nRevenue rose."
    assert summary.artifact_type is ArtifactType.SUMMARY
    assert summary.content == "Executive overview"
    assert "Document summary:" in fake.calls[0]["prompt"]


def test_raptor_generator_links_parents_and_children():
    client, _ = client_with("Cluster summary")
    chunks = [Chunk(doc_id=uuid4(), content="A"), Chunk(doc_id=uuid4(), content="B")]
    chunks[1] = chunks[1].model_copy(update={"doc_id": chunks[0].doc_id})
    parents, children = RaptorGenerator(client, cluster_size=2).generate(chunks)
    assert parents[0].artifact_type is ArtifactType.RAPTOR_SUMMARY
    assert all(child.parent_chunk_id == parents[0].chunk_id for child in children)
    assert parents[0].metadata["child_chunk_ids"] == [str(chunk.chunk_id) for chunk in chunks]


def test_qa_and_factoid_generators_parse_json_artifacts():
    client, fake = client_with('[{"question":"Where?","answer":"APAC"},{"question":"What grew?","answer":"Revenue"},{"question":"How much?","answer":"14%"}]', '["APAC grew 14%", "APAC is a region"]')
    chunk = Chunk(doc_id=uuid4(), content="APAC grew 14%.")
    qa = QAPairGenerator(client).generate(chunk)
    facts = FactoidGenerator(client).generate(chunk)
    assert qa[0].artifact_type is ArtifactType.QA_PAIR
    assert qa[0].content == "Question: Where?\nAnswer: APAC"
    assert all(fact.artifact_type is ArtifactType.FACTOID for fact in facts)
    assert all(call["format"] == "json" for call in fake.calls)


def test_qa_generator_rejects_an_invalid_pair_count():
    client, _ = client_with('[]')
    with __import__("pytest").raises(ValueError, match="between 3 and 5"):
        QAPairGenerator(client).generate(Chunk(doc_id=uuid4(), content="Source text"))