"""Configuration settings for Document Processor using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProcessorSettings(BaseSettings):
    """Configuration for document parsing, semantic chunking, and artifact generation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ollama Host & LLM Configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="URL of the local Ollama LLM server",
    )
    ollama_generation_model: str = Field(
        default="llama3.2",
        description="Primary Ollama model for contextualization and generation",
    )
    ollama_summary_model: str = Field(
        default="llama3.2",
        description="Model used for executive and section summaries",
    )
    ollama_qa_model: str = Field(
        default="qwen2.5:7b",
        description="Model used for high-accuracy QA pair generation",
    )

    # Semantic Chunking Parameters (Chonkie)
    chunk_size: int = Field(
        default=512,
        ge=64,
        le=4096,
        description="Target maximum token length per semantic chunk",
    )
    chunk_overlap: int = Field(
        default=64,
        ge=0,
        le=512,
        description="Overlap token size between semantic chunks",
    )
    similarity_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Similarity boundary threshold for Chonkie semantic splitting",
    )

    # RAPTOR Hierarchical Clustering Parameters
    raptor_cluster_size: int = Field(
        default=5,
        ge=2,
        le=20,
        description="Number of leaf chunks grouped per Tier-1 RAPTOR summary node",
    )

    # Output Directory
    output_dir: str = Field(
        default="./output",
        description="Default folder where parsed artifacts and JSONL logs are stored",
    )


# Singleton instance
settings = ProcessorSettings()
