"""
Test for enhanced event system with async support and error handling.
"""

import asyncio

from app.events import ArticleCreated, ArticleFavorited
from tests.test_event_bus import MockEventBus


def test_async_event_publishing():
    """Test async event publishing and handling."""

    async def run_test():
        test_bus = MockEventBus()

        # Create async handler
        handled_events = []

        async def async_handler(event):
            await asyncio.sleep(0.01)  # Simulate async work
            handled_events.append(event)

        # Subscribe and publish async
        test_bus.subscribe_async(ArticleCreated, async_handler)
        event = ArticleCreated(article_id=1, author_id=2)
        await test_bus.publish_async(event)

        # Assertions
        assert len(test_bus.published_events) == 1
        assert len(handled_events) == 1
        assert test_bus.published_events[0] == event

    asyncio.run(run_test())


def test_error_handling_in_handlers():
    """Test that event bus handles handler errors gracefully."""
    test_bus = MockEventBus()

    # Create handlers - one that fails, one that succeeds
    successful_calls = []

    def failing_handler(event):
        raise Exception("Handler error")

    def successful_handler(event):
        successful_calls.append(event)

    # Subscribe both handlers
    test_bus.subscribe(ArticleCreated, failing_handler)
    test_bus.subscribe(ArticleCreated, successful_handler)

    # Publish event
    event = ArticleCreated(article_id=1, author_id=2)
    test_bus.publish(event)

    # The successful handler should still work despite the failing one
    assert len(successful_calls) == 1
    assert len(test_bus.published_events) == 1


def test_mixed_sync_and_async_handlers():
    """Test that both sync and async handlers work together."""

    async def run_test():
        test_bus = MockEventBus()

        sync_handled = []
        async_handled = []

        def sync_handler(event):
            sync_handled.append(event)

        async def async_handler(event):
            await asyncio.sleep(0.01)
            async_handled.append(event)

        # Subscribe both types
        test_bus.subscribe(ArticleFavorited, sync_handler)
        test_bus.subscribe_async(ArticleFavorited, async_handler)

        # Publish sync
        event1 = ArticleFavorited(article_id=1, user_id=2)
        test_bus.publish(event1)

        # Publish async
        event2 = ArticleFavorited(article_id=2, user_id=3)
        await test_bus.publish_async(event2)

        # Check results
        assert len(sync_handled) == 1  # Only from sync publish
        assert len(async_handled) == 1  # Only from async publish
        assert len(test_bus.published_events) == 2  # Both captured

    asyncio.run(run_test())
