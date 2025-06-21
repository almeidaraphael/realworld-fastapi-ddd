from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config.settings import (
    DatabaseSettings,
    TestDatabaseSettings,
    get_app_settings,
    get_database_settings,
    get_test_database_settings,
)


def get_async_engine() -> AsyncEngine:
    app_settings = get_app_settings()
    settings: DatabaseSettings | TestDatabaseSettings
    if getattr(app_settings, "test_mode", False):
        settings = get_test_database_settings()
    else:
        settings = get_database_settings()
    return create_async_engine(
        str(settings.database_url),
        echo=getattr(settings, "debug", False),
        pool_pre_ping=True,
    )
