import logging

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config.settings import get_app_settings, get_database_settings

_engine_instance: AsyncEngine | None = None
_engine_url: str | None = None


def get_async_engine() -> AsyncEngine:
    """Get or create async database engine with automatic environment detection."""
    global _engine_instance, _engine_url

    settings = get_database_settings()
    app_settings = get_app_settings()
    url = str(settings.database_url)

    # If engine exists but url changed, recreate
    if _engine_instance is not None and _engine_url != url:
        logging.info(
            "Engine singleton recreated: url changed (old url=%s, new url=%s)", _engine_url, url
        )
        _engine_instance = None

    if _engine_instance is not None:
        return _engine_instance

    # Log which environment we're using for debugging
    logging.info(
        "Creating new async engine for environment: %s, database: %s",
        settings.environment.value,
        settings.postgres_db,
    )

    _engine_instance = create_async_engine(
        url,
        echo=app_settings.debug,
        pool_pre_ping=True,
        isolation_level="READ COMMITTED",
    )
    _engine_url = url
    return _engine_instance


def reset_engine() -> None:
    """Reset the engine singleton. Useful for testing."""
    global _engine_instance, _engine_url
    _engine_instance = None
    _engine_url = None
