"""asyncpg connection pool lifecycle management."""

from typing import Any

from src.config import VectorApiSettings


class PostgresPool:
    """Create and close the service's asyncpg connection pool."""

    def __init__(self, settings: VectorApiSettings) -> None:
        self._settings = settings
        self.pool: Any | None = None

    async def connect(self) -> Any:
        """Create the pool on first use and return it."""
        if self.pool is None:
            import asyncpg

            self.pool = await asyncpg.create_pool(
                dsn=self._settings.postgres_dsn,
                min_size=self._settings.postgres_min_connections,
                max_size=self._settings.postgres_max_connections,
            )
        return self.pool

    async def close(self) -> None:
        """Close the active pool, if one has been created."""
        if self.pool is not None:
            await self.pool.close()
            self.pool = None