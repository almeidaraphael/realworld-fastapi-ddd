from contextlib import AbstractAsyncContextManager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.orm.engine import get_async_engine


class AsyncUnitOfWork(AbstractAsyncContextManager["AsyncUnitOfWork"]):
    def __init__(self) -> None:
        self.engine = get_async_engine()
        self.session: AsyncSession = None  # type: ignore[assignment]

    async def __aenter__(self) -> "AsyncUnitOfWork":
        self.session = AsyncSession(self.engine, expire_on_commit=False)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
