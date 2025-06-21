from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.adapters.orm.unit_of_work import AsyncUnitOfWork


@pytest.mark.asyncio
async def test_async_unit_of_work_commit_and_close() -> None:
    """
    GIVEN a new AsyncUnitOfWork context
    WHEN the context is entered and exited without exception
    THEN it should commit and close the session
    """
    fake_engine = MagicMock()
    with patch("app.adapters.orm.unit_of_work.get_async_engine", return_value=fake_engine):
        with patch("app.adapters.orm.unit_of_work.AsyncSession", autospec=True) as mock_session_cls:
            mock_session = AsyncMock()
            mock_session_cls.return_value = mock_session
            uow = AsyncUnitOfWork()
            await uow.__aenter__()
            await uow.__aexit__(None, None, None)
            mock_session.commit.assert_awaited_once()
            mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_unit_of_work_rollback_on_exception() -> None:
    """
    GIVEN a new AsyncUnitOfWork context
    WHEN the context is exited with an exception
    THEN it should rollback and close the session
    """
    fake_engine = MagicMock()
    with patch("app.adapters.orm.unit_of_work.get_async_engine", return_value=fake_engine):
        with patch("app.adapters.orm.unit_of_work.AsyncSession", autospec=True) as mock_session_cls:
            mock_session = AsyncMock()
            mock_session_cls.return_value = mock_session
            uow = AsyncUnitOfWork()
            await uow.__aenter__()
            await uow.__aexit__(Exception, Exception("fail"), None)
            mock_session.rollback.assert_awaited_once()
            mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_unit_of_work_commit_method() -> None:
    """
    GIVEN an AsyncUnitOfWork instance
    WHEN commit is called
    THEN it should await the session's commit method
    """
    fake_engine = MagicMock()
    with patch("app.adapters.orm.unit_of_work.get_async_engine", return_value=fake_engine):
        with patch("app.adapters.orm.unit_of_work.AsyncSession", autospec=True) as mock_session_cls:
            mock_session = AsyncMock()
            mock_session_cls.return_value = mock_session
            uow = AsyncUnitOfWork()
            await uow.__aenter__()
            await uow.commit()
            mock_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_async_unit_of_work_rollback_method() -> None:
    """
    GIVEN an AsyncUnitOfWork instance
    WHEN rollback is called
    THEN it should await the session's rollback method
    """
    fake_engine = MagicMock()
    with patch("app.adapters.orm.unit_of_work.get_async_engine", return_value=fake_engine):
        with patch("app.adapters.orm.unit_of_work.AsyncSession", autospec=True) as mock_session_cls:
            mock_session = AsyncMock()
            mock_session_cls.return_value = mock_session
            uow = AsyncUnitOfWork()
            await uow.__aenter__()
            await uow.rollback()
            mock_session.rollback.assert_awaited()
