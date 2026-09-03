"""Versioned API route registration."""

from fastapi import APIRouter

from src.api.v1 import chunks, documents, health, search

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(documents.router)
api_router.include_router(chunks.router)
api_router.include_router(search.router)
api_router.include_router(health.router)