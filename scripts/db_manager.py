#!/usr/bin/env python3
"""
Database management script for the FastAPI RealWorld demo.

This script helps manage database operations across different environments.
"""

import argparse
import asyncio
import sys
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.orm.engine import get_async_engine
from app.config.settings import Environment, get_database_settings


async def check_database_connection() -> bool:
    """Check if database connection is working."""
    try:
        engine = get_async_engine()
        async with AsyncSession(engine) as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


async def get_database_info() -> dict[str, Any]:
    """Get database information."""
    settings = get_database_settings()
    engine = get_async_engine()

    info = {
        "environment": settings.environment.value,
        "database": settings.postgres_db,
        "host": settings.postgres_host,
        "port": settings.postgres_port,
        "user": settings.postgres_user,
        "url": str(settings.database_url),
        "connected": await check_database_connection(),
    }

    if info["connected"]:
        try:
            async with AsyncSession(engine) as session:
                # Get database version
                result = await session.execute(text("SELECT version()"))
                info["version"] = result.scalar()

                # Get table count
                result = await session.execute(
                    text("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
                )
                info["table_count"] = result.scalar()

        except Exception as e:
            info["error"] = str(e)

    return info


async def reset_database() -> bool:
    """Reset the database by dropping and recreating all tables."""
    try:
        settings = get_database_settings()

        # Safety check - don't allow reset of production database
        if settings.environment == Environment.PRODUCTION:
            print("ERROR: Cannot reset production database!")
            return False

        engine = get_async_engine()
        async with AsyncSession(engine) as session:
            # Drop all tables
            await session.execute(
                text("""
                DROP SCHEMA public CASCADE;
                CREATE SCHEMA public;
                GRANT ALL ON SCHEMA public TO postgres;
                GRANT ALL ON SCHEMA public TO public;
            """)
            )
            await session.commit()
            print("Database reset successfully!")
            return True

    except Exception as e:
        print(f"Database reset failed: {e}")
        return False


def print_database_info(info: dict[str, Any]) -> None:
    """Print database information in a formatted way."""
    print("=== Database Information ===")
    print(f"Environment: {info['environment']}")
    print(f"Database: {info['database']}")
    print(f"Host: {info['host']}:{info['port']}")
    print(f"User: {info['user']}")
    print(f"Connected: {'✓' if info['connected'] else '✗'}")

    if info["connected"]:
        if "version" in info:
            print(f"Version: {info['version'].split(',')[0]}")
        if "table_count" in info:
            print(f"Tables: {info['table_count']}")
    else:
        print("Connection failed - cannot retrieve additional info")

    if "error" in info:
        print(f"Error: {info['error']}")

    print("=" * 30)


async def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Database management script")
    parser.add_argument("command", choices=["info", "check", "reset"], help="Command to execute")
    parser.add_argument(
        "--env",
        choices=["development", "testing", "production"],
        help="Environment to use (overrides auto-detection)",
    )

    args = parser.parse_args()

    # Set environment if specified
    if args.env:
        import os

        os.environ["APP_ENV"] = args.env

    if args.command == "info":
        info = await get_database_info()
        print_database_info(info)

    elif args.command == "check":
        connected = await check_database_connection()
        if connected:
            print("✓ Database connection successful")
            sys.exit(0)
        else:
            print("✗ Database connection failed")
            sys.exit(1)

    elif args.command == "reset":
        settings = get_database_settings()
        print(f"WARNING: This will reset the {settings.environment.value} database!")
        print(f"Database: {settings.postgres_db}")

        if settings.environment == Environment.PRODUCTION:
            print("ERROR: Cannot reset production database!")
            sys.exit(1)

        confirm = input("Are you sure? Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            success = await reset_database()
            sys.exit(0 if success else 1)
        else:
            print("Reset cancelled.")
            sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
