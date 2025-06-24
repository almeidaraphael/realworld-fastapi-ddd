import logging
import os
from logging.config import fileConfig

from sqlalchemy import MetaData
from sqlalchemy.engine import Connection

from alembic import context
from app.config.settings import get_database_settings
from app.domain.articles.orm import metadata as articles_metadata
from app.domain.users.orm import metadata as users_metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Check if DATABASE_URL is provided via environment (from Makefile)
if database_url_from_env := os.getenv("DATABASE_URL"):
    DATABASE_URL = database_url_from_env
    logger = logging.getLogger("alembic.env")
    logger.info(f"[alembic debug] Using DATABASE_URL from environment: {DATABASE_URL}")
else:
    # Fall back to settings detection
    db_settings = get_database_settings()
    DATABASE_URL = str(db_settings.database_url)
    logger = logging.getLogger("alembic.env")
    logger.info(f"[alembic debug] Using DATABASE_URL from settings: {DATABASE_URL}")
    logger.info(f"[alembic debug] Environment: {db_settings.environment}")
    logger.info(f"[alembic debug] Database: {db_settings.postgres_db}")

# Combine all domain metadata for migrations
metadata = MetaData()
for m in [articles_metadata, users_metadata]:
    for table in m.tables.values():
        if table.name not in metadata.tables:
            metadata._add_table(table.name, table.schema, table)

target_metadata = metadata


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
