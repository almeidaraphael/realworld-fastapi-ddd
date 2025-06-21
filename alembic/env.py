import asyncio
from logging.config import fileConfig

from sqlalchemy.engine import Connection
from sqlmodel import SQLModel

from alembic import context
from app.config.settings import get_app_settings, get_database_settings, get_test_database_settings

# Import all model modules so SQLModel.metadata is complete for Alembic

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use test DB settings if TEST_MODE is true in AppSettings, else use dev DB
app_settings = get_app_settings()
if app_settings.test_mode:
    db_settings = get_test_database_settings()
else:
    db_settings = get_database_settings()
DATABASE_URL = str(db_settings.database_url)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine

    connectable = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
