from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.db.postgres import PostgresDatabaseAdapter

engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
)

SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
postgres_adapter = PostgresDatabaseAdapter(engine=engine, session_factory=SessionLocal)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async for session in postgres_adapter.get_session():
        yield session
