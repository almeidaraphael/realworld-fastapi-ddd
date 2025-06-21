from collections.abc import AsyncGenerator, Callable

from sqlmodel.ext.asyncio.session import AsyncSession

from app.adapters.orm.engine import get_async_engine


def get_session() -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    engine = get_async_engine()

    async def _get_session() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSession(engine) as session:
            yield session

    return _get_session
