import logging
import os
import subprocess
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

# Set test environment before any imports that might trigger settings loading
os.environ["APP_ENV"] = "testing"

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from polyfactory.factories.pydantic_factory import ModelFactory
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.orm.engine import get_async_engine, reset_engine
from app.api.users import get_current_user
from app.config.settings import get_database_settings
from app.domain.users.schemas import UserWithToken
from app.main import app
from tests.factories import ArticleAuthorFactory, ArticleFactory, UserReadFactory
from tests.helpers import login_user, register_user

logger = logging.getLogger(__name__)


@pytest.fixture
def user_factory() -> ModelFactory:
    """Factory for generating UserRead Pydantic models."""
    return UserReadFactory()


@pytest.fixture
def article_factory() -> ModelFactory:
    """Factory for generating ArticleCreate Pydantic models."""
    return ArticleFactory()


@pytest.fixture
def article_author_factory() -> ModelFactory:
    """Factory for generating ArticleAuthorOut Pydantic models."""
    return ArticleAuthorFactory()


@pytest.fixture
def test_password() -> str:
    """Standard password to use in tests."""
    return "securePassword123!"


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for FastAPI app using ASGITransport."""
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac


@pytest_asyncio.fixture(autouse=True, scope="function")
async def clean_tables() -> AsyncGenerator[None, None]:
    """Delete all rows from all tables before each test for idempotency."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        from app.domain.articles.orm import article_favorite_table, article_table
        from app.domain.users.orm import follower_table, user_table

        for table in [article_favorite_table, article_table, follower_table, user_table]:
            await conn.execute(delete(table))
    yield


@pytest.fixture
def mock_repo(mocker: Any) -> Any:
    """Mock UserRepository for unit tests."""
    repo = mocker.patch("app.service_layer.users.services.UserRepository")
    return repo


@pytest.fixture
def mock_uow(mocker: Any) -> tuple[Any, Any]:
    """Mock AsyncUnitOfWork and session for unit tests."""
    uow = mocker.patch("app.service_layer.users.services.AsyncUnitOfWork")
    mock_session = AsyncMock()
    uow.return_value.__aenter__.return_value.session = mock_session
    return uow, mock_session


@pytest.fixture
def user_read_factory() -> ModelFactory:
    """Factory for generating UserRead Pydantic models."""
    return UserReadFactory()


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Async SQLAlchemy session for database access in tests."""
    engine = get_async_engine()
    async with AsyncSession(engine) as session:
        yield session


@pytest.fixture
def patch_uow_profiles(mocker: Any) -> Any:
    """Mock AsyncUnitOfWork for profiles service."""
    patcher = mocker.patch("app.service_layer.profiles.services.AsyncUnitOfWork")
    mock_ctx = patcher.return_value.__aenter__.return_value
    return patcher, mock_ctx


@pytest.fixture
def patch_repo_profiles(mocker: Any) -> Any:
    """Mock UserRepository for profiles service."""
    repo = MagicMock()
    repo.get_by_username_or_email = AsyncMock(return_value=None)
    repo.is_following = AsyncMock(return_value=False)
    patcher = mocker.patch("app.service_layer.profiles.services.UserRepository", return_value=repo)
    return patcher, repo


@pytest.fixture
def patch_uow_users(mocker: Any) -> Any:
    """Mock AsyncUnitOfWork for users service."""
    patcher = mocker.patch("app.service_layer.users.services.AsyncUnitOfWork")
    mock_ctx = patcher.return_value.__aenter__.return_value
    return patcher, mock_ctx


@pytest.fixture
def patch_repo_users(mocker: Any, fake_user: MagicMock) -> tuple[Any, Any]:
    """Mock UserRepository for users service with a fake user."""
    repo = MagicMock()
    repo.get_by_username_or_email = AsyncMock(return_value=fake_user)
    patcher = mocker.patch("app.service_layer.users.services.UserRepository", return_value=repo)
    return patcher, repo


@pytest.fixture
def fake_user():
    """Fake user object for dependency overrides in tests."""
    return UserWithToken(
        id=1,
        username="johndoe",
        email="johndoe@email.com",
        bio="bio",
        image="img",
        token="token",
    )


@pytest.fixture
def override_auth(fake_user):
    """Override FastAPI auth dependency with a fake user."""
    app.dependency_overrides[get_current_user] = lambda: fake_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True, scope="function")
def reset_async_engine():
    """Reset the async engine singleton between tests to avoid cross-test contamination."""
    reset_engine()
    yield
    reset_engine()


@pytest.fixture
def register_user_fixture():
    """Fixture for registering a user via the API in tests."""
    return register_user


@pytest.fixture
def login_user_fixture():
    """Fixture for logging in a user via the API in tests."""
    return login_user


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Apply database migrations for tests."""
    db_settings = get_database_settings()
    db_url = str(db_settings.database_url)
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    env["DATABASE_URL"] = db_url
    subprocess.run(["alembic", "upgrade", "head"], check=True, env=env)
