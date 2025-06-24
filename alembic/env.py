import logging
from logging.config import fileConfig

from sqlalchemy.engine import Connection
from sqlmodel import SQLModel

from alembic import context
from app.config.settings import get_database_settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_settings = get_database_settings()
DATABASE_URL = str(db_settings.database_url)
logger = logging.getLogger("alembic.env")
logger.info(f"[alembic debug] DATABASE_URL: {DATABASE_URL}")

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
    import asyncio

    asyncio.run(run_migrations_online())
