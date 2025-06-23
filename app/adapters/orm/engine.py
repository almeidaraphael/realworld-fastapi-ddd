import logging
import os
import sys

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config.settings import get_database_settings

_engine_instance: AsyncEngine | None = None
_engine_url: str | None = None


def get_async_engine() -> AsyncEngine:
    global _engine_instance, _engine_url
    env_file = ".env.test" if any("pytest" in arg for arg in sys.argv) else ".env"
    os.environ["ENV_FILE"] = env_file
    settings = get_database_settings()
    url = str(settings.database_url)
    # If engine exists but url changed, recreate
    if _engine_instance is not None and _engine_url != url:
        logging.warning(
            "Engine singleton recreated: url changed (old url=%s, new url=%s)", _engine_url, url
        )
        _engine_instance = None
    if _engine_instance is not None:
        return _engine_instance
    if env_file == ".env":
        logging.warning("Engine created outside of test mode! Using production/dev DB.")
    _engine_instance = create_async_engine(
        url,
        echo=getattr(settings, "debug", False),
        pool_pre_ping=True,
        isolation_level="READ COMMITTED",
    )
    _engine_url = url
    return _engine_instance
