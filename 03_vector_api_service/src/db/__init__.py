"""Vector storage repository abstractions and backend factories."""

from .base import BaseVectorRepository
from .factory import RepositoryFactory

__all__ = ["BaseVectorRepository", "RepositoryFactory"]