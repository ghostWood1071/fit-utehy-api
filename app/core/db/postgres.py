from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession

from app.core.db.base import DatabaseAdapter


class PostgresDatabaseAdapter(DatabaseAdapter):
    def __init__(self, engine: AsyncEngine, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._engine = engine
        self._session_factory = session_factory

    async def get_session(self) -> AsyncIterator[AsyncSession]:
        session = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def healthcheck(self) -> bool:
        async with self._engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            return result.scalar_one() == 1
