import logging
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from polyfactory.factories.pydantic_factory import ModelFactory
from sqlalchemy import delete
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.adapters.orm.engine import get_async_engine
from app.main import app
from tests.factories import UserFactory, UserReadFactory

logger = logging.getLogger(__name__)


@pytest.fixture
def user_factory() -> ModelFactory:
    return UserFactory()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac


@pytest_asyncio.fixture(autouse=True, scope="function")
async def clean_tables() -> AsyncGenerator[None, None]:
    """Delete all rows from all tables before each test for idempotency."""
    engine = get_async_engine()
    logger.info(f"[DEBUG] clean_tables: Using engine {engine}")
    async with engine.begin() as conn:
        for table in reversed(SQLModel.metadata.sorted_tables):
            logger.info(f"[DEBUG] clean_tables: Deleting table {table}")
            await conn.execute(delete(table))
    yield


@pytest.fixture
def mock_repo(mocker: Any) -> Any:
    repo = mocker.patch("app.service_layer.users.services.UserRepository")
    return repo


@pytest.fixture
def mock_uow(mocker: Any) -> tuple[Any, Any]:
    uow = mocker.patch("app.service_layer.users.services.AsyncUnitOfWork")
    mock_session = AsyncMock()
    uow.return_value.__aenter__.return_value.session = mock_session
    return uow, mock_session


@pytest.fixture
def user_read_factory() -> ModelFactory:
    return UserReadFactory()


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    engine = get_async_engine()
    logger.info(f"[DEBUG] async_session: Using engine {engine}")
    async with AsyncSession(engine) as session:
        logger.info(f"[DEBUG] async_session: Yielding session {session}")
        yield session


# PATCH_UOW for profiles service
@pytest.fixture
def patch_uow_profiles(mocker: Any) -> Any:
    patcher = mocker.patch("app.service_layer.profiles.services.AsyncUnitOfWork")
    mock_ctx = patcher.return_value.__aenter__.return_value
    return patcher, mock_ctx


# PATCH_REPO for profiles service
@pytest.fixture
def patch_repo_profiles(mocker: Any) -> Any:
    repo = MagicMock()
    repo.get_by_username_or_email = AsyncMock(return_value=None)
    repo.is_following = AsyncMock(return_value=False)
    patcher = mocker.patch("app.service_layer.profiles.services.UserRepository", return_value=repo)
    return patcher, repo


# PATCH_UOW for users service (if not already present)
@pytest.fixture
def patch_uow_users(mocker: Any) -> Any:
    patcher = mocker.patch("app.service_layer.users.services.AsyncUnitOfWork")
    mock_ctx = patcher.return_value.__aenter__.return_value
    return patcher, mock_ctx


# PATCH_REPO for users service (if not already present)
@pytest.fixture
def patch_repo_users(mocker: Any, fake_user: MagicMock) -> tuple[Any, Any]:
    repo = MagicMock()
    repo.get_by_username_or_email = AsyncMock(return_value=fake_user)
    patcher = mocker.patch("app.service_layer.users.services.UserRepository", return_value=repo)
    return patcher, repo
