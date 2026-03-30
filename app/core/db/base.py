from abc import ABC, abstractmethod
from typing import AsyncIterator, Protocol


class AsyncSessionProtocol(Protocol):
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
    async def close(self) -> None: ...


class DatabaseAdapter(ABC):
    @abstractmethod
    async def get_session(self) -> AsyncIterator[AsyncSessionProtocol]:
        """Provide an async database session."""

    @abstractmethod
    async def healthcheck(self) -> bool:
        """Check connectivity to backing database."""
