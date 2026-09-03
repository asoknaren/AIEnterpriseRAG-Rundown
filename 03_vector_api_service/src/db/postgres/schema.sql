CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE IF NOT EXISTS documents (
    doc_id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    source_type VARCHAR(32) NOT NULL,
    file_path TEXT,
    sha256_hash VARCHAR(64) UNIQUE NOT NULL,
    total_pages INTEGER NOT NULL DEFAULT 1,
    doc_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id UUID PRIMARY KEY,
    doc_id UUID NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,
    parent_chunk_id UUID,
    artifact_type VARCHAR(32) NOT NULL,
    content TEXT NOT NULL,
    raw_content TEXT,
    embedding vector(1536),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_document_chunks_doc_id ON document_chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_artifact_type ON document_chunks(artifact_type);
CREATE INDEX IF NOT EXISTS idx_document_chunks_parent_id ON document_chunks(parent_chunk_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw
    ON document_chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);