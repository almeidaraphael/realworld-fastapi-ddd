import logging
import os
import subprocess
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock

# Set test environment before any imports that might trigger settings loading
os.environ["APP_ENV"] = "testing"

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from polyfactory.factories.pydantic_factory import ModelFactory
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.orm.engine import get_async_engine, reset_engine
from app.api.users import get_current_user
from app.config.settings import get_database_settings
from app.domain.users.schemas import UserWithToken
from app.main import app
from tests.factories import ArticleAuthorFactory, ArticleFactory, UserReadFactory
from tests.helpers import login_user, register_user

logger = logging.getLogger(__name__)


# ============================================================================
# Database Management Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Session-scoped database engine that persists across tests."""
    engine = get_async_engine()
    yield engine
    await engine.dispose()


@asynccontextmanager
async def db_transaction(engine):
    """
    Context manager for database transactions in tests.

    Creates a transaction that can be rolled back for test isolation.
    """
    async with engine.begin() as conn:
        # Start a savepoint for nested transactions
        savepoint = await conn.begin_nested()
        try:
            # Create a session bound to this connection
            async with AsyncSession(
                bind=conn, expire_on_commit=False, autoflush=False, autocommit=False
            ) as session:
                yield session
        finally:
            # Always rollback the savepoint
            await savepoint.rollback()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """
    Function-scoped database session with automatic transaction rollback.

    This provides complete test isolation by rolling back all changes
    made during the test.
    """
    async with db_transaction(db_engine) as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def clean_tables_fast():
    """
    Fast table cleanup using TRUNCATE CASCADE.

    More efficient than DELETE as it doesn't scan rows and resets sequences.
    Uses CASCADE to handle foreign key constraints automatically.
    """
    engine = get_async_engine()

    # Table names in dependency order (children first)
    table_names = ["comment", "article_favorite", "article", "follower", "user"]

    async with engine.begin() as conn:
        # Disable foreign key checks temporarily for faster cleanup
        await conn.execute(text("SET session_replication_role = replica;"))

        try:
            # Truncate all tables in one statement for maximum efficiency
            tables_sql = ", ".join(table_names)
            await conn.execute(text(f"TRUNCATE TABLE {tables_sql} RESTART IDENTITY CASCADE;"))
        finally:
            # Re-enable foreign key checks
            await conn.execute(text("SET session_replication_role = DEFAULT;"))


@pytest_asyncio.fixture(autouse=True, scope="function")
async def db_isolation():
    """
    Automatic database isolation for every test function.

    Uses the fastest available cleanup method and resets the engine
    to prevent connection pool issues.
    """
    # Reset engine before test to ensure clean state
    reset_engine()

    yield

    # Fast cleanup after test with proper error handling
    try:
        engine = get_async_engine()

        # Table names in dependency order (children first) - properly quoted for PostgreSQL
        table_names = ['"comment"', '"article_favorite"', '"article"', '"follower"', '"user"']

        # Use a fresh connection for cleanup to avoid transaction state issues
        async with engine.connect() as conn:
            # Start a new transaction for cleanup
            async with conn.begin():
                try:
                    # Truncate all tables in one statement for maximum efficiency
                    tables_sql = ", ".join(table_names)
                    await conn.execute(
                        text(f"TRUNCATE TABLE {tables_sql} RESTART IDENTITY CASCADE;")
                    )
                except Exception as e:
                    # If TRUNCATE fails, fall back to DELETE
                    logger.warning(f"TRUNCATE failed ({e}), falling back to DELETE")
                    for table_name in reversed(table_names):
                        try:
                            await conn.execute(text(f"DELETE FROM {table_name};"))
                        except Exception as del_e:
                            logger.warning(f"DELETE from {table_name} failed: {del_e}")
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")
        # Continue anyway - don't let cleanup errors break tests

    # Reset engine after test to prevent cross-test contamination
    reset_engine()


# ============================================================================
# Factory Fixtures
# ============================================================================


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


# ============================================================================
# HTTP Client Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for FastAPI app using ASGITransport."""
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac


# ============================================================================
# Session Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async SQLAlchemy session for database access in tests.

    Configured with expire_on_commit=False for better test reliability.
    Note: Prefer using db_session fixture for new tests as it provides
    automatic transaction rollback.
    """
    engine = get_async_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


# ============================================================================
# Mock Fixtures for Unit Tests
# ============================================================================


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


# ============================================================================
# Enhanced Database Fixtures for Specific Test Types
# ============================================================================


@pytest.fixture
def db_transactional_session(db_engine):
    """
    Provides a transactional session that can be used within tests
    for manual transaction control.
    """
    return db_transaction


@pytest.fixture
def db_isolated_session():
    """
    Provides a completely isolated database session for tests that
    need to verify database state without interference.
    """

    async def _get_isolated_session():
        # Create a new engine connection
        engine = get_async_engine()
        async with AsyncSession(engine, expire_on_commit=False) as session:
            yield session

    return _get_isolated_session


@pytest.mark.database
def pytest_configure(config):
    """Configure markers for database tests."""
    config.addinivalue_line("markers", "database: mark test as requiring database access")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")


# ============================================================================
# Test Utilities and Helpers
# ============================================================================


@pytest.fixture
def db_cleanup_strategy():
    """
    Provides different cleanup strategies for tests with specific needs.

    Returns a dictionary of cleanup functions:
    - 'fast': TRUNCATE CASCADE (default)
    - 'selective': DELETE specific tables
    - 'none': No cleanup (manual control)
    """

    async def fast_cleanup():
        await clean_tables_fast()

    async def selective_cleanup(table_names: list[str]):
        engine = get_async_engine()
        async with engine.begin() as conn:
            for table_name in reversed(table_names):  # Reverse for FK constraints
                await conn.execute(text(f"DELETE FROM {table_name};"))

    async def no_cleanup():
        pass

    return {
        "fast": fast_cleanup,
        "selective": selective_cleanup,
        "none": no_cleanup,
    }
