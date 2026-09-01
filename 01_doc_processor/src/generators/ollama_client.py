"""Small resilient boundary around the Ollama generation API."""

from collections.abc import Callable
from typing import Any

from src.config import ProcessorSettings, settings


class OllamaGeneratorClient:
    """Generate deterministic text responses, retrying a fallback model once."""

    def __init__(self, processor_settings: ProcessorSettings = settings, client_factory: Callable[..., Any] | None = None) -> None:
        self._settings = processor_settings
        self._client_factory = client_factory or self._create_client

    @staticmethod
    def _create_client(**kwargs: Any) -> Any:
        from ollama import Client

        return Client(**kwargs)

    @property
    def summary_model(self) -> str:
        """Return the configured model for document and section summaries."""
        return self._settings.ollama_summary_model

    @property
    def qa_model(self) -> str:
        """Return the configured model for structured QA generation."""
        return self._settings.ollama_qa_model

    def generate(self, prompt: str, model: str | None = None, fallback_model: str | None = None, json_mode: bool = False) -> str:
        """Generate text, retrying the fallback model when the primary fails."""
        client = self._client_factory(host=self._settings.ollama_base_url)
        primary_model = model or self._settings.ollama_generation_model
        models = [primary_model]
        if fallback_model and fallback_model != primary_model:
            models.append(fallback_model)
        last_error: Exception | None = None
        for candidate in models:
            try:
                response = client.generate(model=candidate, prompt=prompt, stream=False, format="json" if json_mode else None)
                return response.response
            except Exception as error:
                last_error = error
        raise RuntimeError("Ollama generation failed for all configured models") from last_error