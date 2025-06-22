from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
import os

from app.config.settings import (
    DatabaseSettings,
    TestDatabaseSettings,
    get_app_settings,
    get_database_settings,
    get_test_database_settings,
)

_engine_instance: AsyncEngine | None = None
_engine_url: str | None = None
_engine_test_mode: bool | None = None


def get_async_engine() -> AsyncEngine:
    global _engine_instance, _engine_url, _engine_test_mode
    app_settings = get_app_settings()
    test_mode = getattr(app_settings, "test_mode", False)
    settings: DatabaseSettings | TestDatabaseSettings
    if test_mode:
        settings = get_test_database_settings()
    else:
        settings = get_database_settings()
    url = str(settings.database_url)
    # If engine exists but url or test_mode changed, recreate
    if (
        _engine_instance is not None
        and (_engine_url != url or _engine_test_mode != test_mode)
    ):
        print(f"[WARNING] Engine singleton recreated: url/test_mode changed (old url={_engine_url}, new url={url}, old test_mode={_engine_test_mode}, new test_mode={test_mode})")
        _engine_instance = None
    if _engine_instance is not None:
        return _engine_instance
    if not test_mode:
        print("[WARNING] Engine created with TEST_MODE not set! Using production DB.")
    _engine_instance = create_async_engine(
        url,
        echo=getattr(settings, "debug", False),
        pool_pre_ping=True,
        isolation_level="READ COMMITTED",
    )
    _engine_url = url
    _engine_test_mode = test_mode
    return _engine_instance
