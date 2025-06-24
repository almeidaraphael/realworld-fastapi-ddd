import logging
from contextlib import AbstractAsyncContextManager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.orm.engine import get_async_engine

logger = logging.getLogger(__name__)


class AsyncUnitOfWork(AbstractAsyncContextManager["AsyncUnitOfWork"]):
    """
    Async Unit of Work pattern implementation.

    Handles transaction management and ensures proper session lifecycle.
    Sessions are configured with:
    - expire_on_commit=False: Keep objects usable after commit
    - autoflush=True: Auto-flush before queries (default, explicit for clarity)
    """

    def __init__(self) -> None:
        self.engine = get_async_engine()
        self.session: AsyncSession = None  # type: ignore[assignment]

    async def __aenter__(self) -> "AsyncUnitOfWork":
        self.session = AsyncSession(self.engine, expire_on_commit=False, autoflush=True)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        try:
            if exc_type:
                logger.debug("Rolling back transaction due to exception: %s", exc_val)
                await self.session.rollback()
            else:
                logger.debug("Committing transaction")
                await self.session.commit()
        except Exception as e:
            logger.error("Error during transaction cleanup: %s", e)
            try:
                await self.session.rollback()
            except Exception as rollback_error:
                logger.error("Error during rollback: %s", rollback_error)
            raise
        finally:
            await self.session.close()

    async def commit(self) -> None:
        """Manually commit the current transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Manually rollback the current transaction."""
        await self.session.rollback()
