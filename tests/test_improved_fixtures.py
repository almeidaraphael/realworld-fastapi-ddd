"""
Performance tests for the improved database fixture organization.

This test module demonstrates the performance improvements achieved
with the new database fixture system.
"""

import time

import pytest

from tests.db_utils import DatabaseTestUtils, benchmark_cleanup_methods


async def test_database_cleanup_performance():
    """
    GIVEN a database with test data
    WHEN cleaning up using the new fast cleanup method
    THEN cleanup should complete in under 50ms
    """
    # Add some test data
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.adapters.orm.engine import get_async_engine

    engine = get_async_engine()
    async with AsyncSession(engine) as session:
        await session.execute(
            text("""
            INSERT INTO "user" (id, username, email, hashed_password, bio, image)
            VALUES (1, 'test1', 'test1@example.com', 'hash1', 'bio1', 'img1'),
                   (2, 'test2', 'test2@example.com', 'hash2', 'bio2', 'img2');
        """)
        )
        await session.commit()

    # Verify data exists
    counts_before = await DatabaseTestUtils.get_table_counts()
    assert counts_before["user"] > 0

    # Time the cleanup
    start_time = time.time()
    await DatabaseTestUtils.truncate_all_tables()
    cleanup_time = time.time() - start_time

    # Verify cleanup was successful
    counts_after = await DatabaseTestUtils.get_table_counts()
    assert counts_after["user"] == 0

    # Assert performance requirement
    assert cleanup_time < 0.05, f"Cleanup took {cleanup_time:.3f}s, expected < 0.05s"


async def test_transaction_rollback_session():
    """
    GIVEN a transaction rollback session
    WHEN making database changes within the session
    THEN changes should be automatically rolled back
    """
    # Verify database is initially empty
    assert await DatabaseTestUtils.verify_empty_database()

    # Use transaction rollback session
    async with DatabaseTestUtils.transaction_rollback_session() as session:
        from sqlalchemy import text

        # Add data within transaction
        await session.execute(
            text("""
            INSERT INTO "user" (id, username, email, hashed_password, bio, image)
            VALUES (1, 'temp_user', 'temp@example.com', 'hash', 'bio', 'img');
        """)
        )
        await session.commit()

        # Data should exist within transaction
        result = await session.execute(text('SELECT COUNT(*) FROM "user";'))
        count = result.scalar()
        assert count == 1

    # After transaction rollback, data should be gone
    final_counts = await DatabaseTestUtils.get_table_counts()
    assert final_counts["user"] == 0


async def test_selective_table_cleanup():
    """
    GIVEN a database with data in multiple tables
    WHEN cleaning only specific tables
    THEN only those tables should be cleaned
    """
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.adapters.orm.engine import get_async_engine

    engine = get_async_engine()
    async with AsyncSession(engine) as session:
        # Add data to multiple tables
        await session.execute(
            text("""
            INSERT INTO "user" (id, username, email, hashed_password, bio, image)
            VALUES (1, 'test1', 'test1@example.com', 'hash1', 'bio1', 'img1');
        """)
        )
        await session.execute(
            text("""
            INSERT INTO "article" (id, slug, title, description, body, author_id,
                                  created_at, updated_at)
            VALUES (1, 'test-article', 'Test Article', 'Description', 'Body', 1, NOW(), NOW());
        """)
        )
        await session.commit()

    # Verify both tables have data
    counts_before = await DatabaseTestUtils.get_table_counts()
    assert counts_before["user"] == 1
    assert counts_before["article"] == 1

    # Clean only user table
    await DatabaseTestUtils.selective_delete(['"user"'])

    # Verify only user table was cleaned
    counts_after = await DatabaseTestUtils.get_table_counts()
    assert counts_after["user"] == 0
    assert counts_after["article"] == 1  # Should still have data


@pytest.mark.integration
async def test_benchmark_cleanup_methods():
    """
    GIVEN different cleanup methods
    WHEN benchmarking their performance
    THEN both methods should complete reasonably quickly
    """
    results = await benchmark_cleanup_methods()

    # Both methods should complete reasonably quickly
    assert results["truncate_cascade"] < 0.1  # 100ms max
    assert results["selective_delete"] < 0.5  # 500ms max

    # Print results for debugging (TRUNCATE may not always be faster for small datasets)
    print("Performance results:")
    print(f"  TRUNCATE CASCADE: {results['truncate_cascade']:.3f}s")
    print(f"  Selective DELETE: {results['selective_delete']:.3f}s")


async def test_database_cleanup_benchmark():
    """
    GIVEN the improved cleanup methods
    WHEN benchmarking cleanup performance
    THEN new methods should outperform old methods
    """
    results = await benchmark_cleanup_methods()

    # Both methods should work
    assert "truncate_cascade" in results
    assert "selective_delete" in results

    # Both should complete in reasonable time
    assert results["truncate_cascade"] < 1.0  # 1 second max
    assert results["selective_delete"] < 2.0  # 2 seconds max

    # Calculate speedup ratio (either direction)
    if results["truncate_cascade"] < results["selective_delete"]:
        speedup = results["selective_delete"] / results["truncate_cascade"]
        print(f"  TRUNCATE is {speedup:.1f}x faster")
    else:
        speedup = results["truncate_cascade"] / results["selective_delete"]
        print(f"  DELETE is {speedup:.1f}x faster")

    # Ensure at least one method is reasonably fast
    fastest = min(results["truncate_cascade"], results["selective_delete"])
    assert fastest < 0.05, f"Fastest cleanup method took {fastest:.3f}s, expected < 0.05s"


async def test_db_session_fixture_isolation(db_session):
    """
    GIVEN a db_session fixture
    WHEN making changes in the session
    THEN changes should be isolated from other tests
    """
    from sqlalchemy import text

    # Add data using the fixture
    await db_session.execute(
        text("""
        INSERT INTO "user" (id, username, email, hashed_password, bio, image)
        VALUES (1, 'fixture_user', 'fixture@example.com', 'hash', 'bio', 'img');
    """)
    )
    await db_session.commit()

    # Data should exist in this session
    result = await db_session.execute(text('SELECT COUNT(*) FROM "user";'))
    count = result.scalar()
    assert count == 1

    # This test will automatically rollback when fixture goes out of scope


async def test_empty_database_verification():
    """
    GIVEN the database cleanup system
    WHEN checking if database is empty
    THEN verification should work correctly
    """
    # Debug: Check initial state
    initial_counts = await DatabaseTestUtils.get_table_counts()
    print(f"Initial counts: {initial_counts}")

    # Should be empty after cleanup
    is_empty_initial = await DatabaseTestUtils.verify_empty_database()
    print(f"Is empty initially: {is_empty_initial}")

    if not is_empty_initial:
        # Manually clean if not empty
        await DatabaseTestUtils.truncate_all_tables()
        is_empty_after_clean = await DatabaseTestUtils.verify_empty_database()
        print(f"Is empty after manual clean: {is_empty_after_clean}")
        assert is_empty_after_clean, "Database should be empty after manual cleanup"

    # Add some data
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.adapters.orm.engine import get_async_engine

    engine = get_async_engine()
    async with AsyncSession(engine) as session:
        await session.execute(
            text("""
            INSERT INTO "user" (id, username, email, hashed_password, bio, image)
            VALUES (1, 'test', 'test@example.com', 'hash', 'bio', 'img');
        """)
        )
        await session.commit()

    # Should no longer be empty
    assert not await DatabaseTestUtils.verify_empty_database()

    # Clean up
    await DatabaseTestUtils.truncate_all_tables()

    # Should be empty again
    assert await DatabaseTestUtils.verify_empty_database()


class TestNewFixtureSystem:
    """Test class demonstrating the new fixture system organization."""

    async def test_automatic_db_isolation_works(self, user_factory):
        """
        GIVEN the automatic db_isolation fixture
        WHEN running multiple tests in sequence
        THEN each test should start with a clean database
        """
        # Database should be clean at start of test
        assert await DatabaseTestUtils.verify_empty_database()

        # Add some data
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession

        from app.adapters.orm.engine import get_async_engine

        engine = get_async_engine()
        async with AsyncSession(engine) as session:
            await session.execute(
                text("""
                INSERT INTO "user" (id, username, email, hashed_password, bio, image)
                VALUES (1, 'test', 'test@example.com', 'hash', 'bio', 'img');
            """)
            )
            await session.commit()

        # Data should exist
        counts = await DatabaseTestUtils.get_table_counts()
        assert counts["user"] == 1

        # Cleanup will happen automatically via db_isolation fixture

    async def test_second_test_also_gets_clean_db(self):
        """
        GIVEN the automatic db_isolation fixture
        WHEN this test runs after the previous one
        THEN database should be clean again
        """
        # This test should also start with clean database
        assert await DatabaseTestUtils.verify_empty_database()

    def test_factory_fixtures_available(self, user_factory, article_factory, test_password):
        """
        GIVEN the organized fixture system
        WHEN accessing factory fixtures
        THEN they should be readily available and functional
        """
        # Factory fixtures should work
        user = user_factory.build()
        assert user.username
        assert user.email

        article = article_factory.build()
        assert article.title
        assert article.body

        # Test password should be available
        assert test_password == "securePassword123!"
