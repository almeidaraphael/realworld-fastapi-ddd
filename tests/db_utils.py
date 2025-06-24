"""
Database test utilities for efficient test database management.

This module provides utilities for fast database operations in tests,
including performance monitoring and advanced cleanup strategies.
"""

import time
from contextlib import asynccontextmanager
from typing import Any, Callable

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.orm.engine import get_async_engine


class DatabaseTestUtils:
    """Utility class for database operations in tests."""

    @staticmethod
    async def truncate_all_tables() -> None:
        """
        Efficiently truncate all tables using a single SQL statement.

        This is the fastest way to clean the database between tests.
        """
        engine = get_async_engine()

        # Table names in dependency order (children first) - properly quoted for PostgreSQL
        table_names = ['"comment"', '"article_favorite"', '"article"', '"follower"', '"user"']

        # Use connect() instead of begin() to avoid transaction state issues
        async with engine.connect() as conn:
            async with conn.begin():
                try:
                    # Truncate all tables in one statement for maximum efficiency
                    tables_sql = ", ".join(table_names)
                    await conn.execute(
                        text(f"TRUNCATE TABLE {tables_sql} RESTART IDENTITY CASCADE;")
                    )
                except Exception:
                    # If TRUNCATE fails, fall back to DELETE
                    for table_name in reversed(table_names):
                        await conn.execute(text(f"DELETE FROM {table_name};"))

    @staticmethod
    async def selective_delete(table_names: list[str]) -> None:
        """
        Delete data from specific tables only.

        Useful when you need to clean only certain tables while preserving
        others for test setup.

        Args:
            table_names: List of table names to delete from (should be properly quoted)
        """
        engine = get_async_engine()
        async with engine.connect() as conn:
            async with conn.begin():
                # Delete in reverse order to handle foreign key constraints
                for table_name in reversed(table_names):
                    # Ensure table name is properly quoted if it's not already
                    quoted_name = table_name if table_name.startswith('"') else f'"{table_name}"'
                    await conn.execute(text(f"DELETE FROM {quoted_name};"))

    @staticmethod
    async def get_table_counts() -> dict[str, int]:
        """
        Get row counts for all tables.

        Useful for debugging test isolation issues.
        """
        engine = get_async_engine()
        table_names = ['"user"', '"follower"', '"article"', '"article_favorite"', '"comment"']
        counts = {}

        async with engine.connect() as conn:
            for table_name in table_names:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
                # Use unquoted name as dictionary key for easier access
                key = table_name.strip('"')
                counts[key] = result.scalar()

        return counts

    @staticmethod
    async def verify_empty_database() -> bool:
        """
        Verify that all tables are empty.

        Returns True if database is clean, False otherwise.
        """
        counts = await DatabaseTestUtils.get_table_counts()
        return all(count == 0 for count in counts.values())

    @staticmethod
    @asynccontextmanager
    async def transaction_rollback_session():
        """
        Provides a session that will rollback all changes at the end.

        This is the most isolated way to run tests - all changes are
        automatically rolled back.
        """
        engine = get_async_engine()
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


class TestPerformanceMonitor:
    """Monitor and log test database performance."""

    def __init__(self):
        self.cleanup_times: list[float] = []
        self.setup_times: list[float] = []

    @asynccontextmanager
    async def time_operation(self, operation_name: str):
        """Time a database operation and log the results."""
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time

            if operation_name == "cleanup":
                self.cleanup_times.append(duration)
            elif operation_name == "setup":
                self.setup_times.append(duration)

            # Log slow operations
            if duration > 0.1:  # 100ms threshold
                print(f"SLOW {operation_name}: {duration:.3f}s")

    def get_stats(self) -> dict[str, Any]:
        """Get performance statistics."""

        def _stats(times: list[float]) -> dict[str, float]:
            if not times:
                return {"count": 0, "avg": 0, "min": 0, "max": 0}
            return {
                "count": len(times),
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
            }

        return {
            "cleanup": _stats(self.cleanup_times),
            "setup": _stats(self.setup_times),
        }


# Global performance monitor instance
perf_monitor = TestPerformanceMonitor()


async def benchmark_cleanup_methods() -> dict[str, float]:
    """
    Benchmark different cleanup methods to find the fastest.

    Returns timing results for different cleanup strategies.
    """

    # Create some test data first
    engine = get_async_engine()
    async with AsyncSession(engine) as session:
        # Add some test data
        await session.execute(
            text("""
            INSERT INTO "user" (id, username, email, hashed_password, bio, image)
            VALUES (1, 'test1', 'test1@example.com', 'hash1', 'bio1', 'img1'),
                   (2, 'test2', 'test2@example.com', 'hash2', 'bio2', 'img2');
        """)
        )
        await session.commit()

    results = {}

    # Test TRUNCATE CASCADE method
    start = time.time()
    await DatabaseTestUtils.truncate_all_tables()
    results["truncate_cascade"] = time.time() - start

    # Add data again for next test
    async with AsyncSession(engine) as session:
        await session.execute(
            text("""
            INSERT INTO "user" (id, username, email, hashed_password, bio, image)
            VALUES (1, 'test1', 'test1@example.com', 'hash1', 'bio1', 'img1'),
                   (2, 'test2', 'test2@example.com', 'hash2', 'bio2', 'img2');
        """)
        )
        await session.commit()

    # Test selective DELETE method
    start = time.time()
    await DatabaseTestUtils.selective_delete(
        ["user", "article", "comment", "follower", "article_favorite"]
    )
    results["selective_delete"] = time.time() - start

    return results


def create_test_data_factory(factory_class: type) -> Callable:
    """
    Create a factory function for generating test data.

    This helps standardize test data creation across test files.
    """

    def _factory(**overrides):
        return factory_class.build(**overrides)

    return _factory
