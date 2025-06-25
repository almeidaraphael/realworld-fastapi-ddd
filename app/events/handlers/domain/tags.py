"""
Event handlers for tag domain events.
Handles tag lifecycle events including creation, usage, and trending detection.
"""

import logging

from app.events import (
    PopularTagDetected,
    TagCreated,
    TagRemoved,
    TagUsed,
    shared_event_bus,
)

logger = logging.getLogger(__name__)


async def handle_tag_created(event: TagCreated) -> None:
    """Handle tag creation event - could index for search, initialize metadata, etc."""
    logger.info(f"TagCreated: tag_name={event.tag_name}, article_id={event.article_id}, author_id={event.author_id}")
    # Simulate async operations like indexing for search
    import asyncio
    await asyncio.sleep(0.01)


async def handle_tag_used(event: TagUsed) -> None:
    """Handle tag usage event - could update usage statistics, improve recommendations, etc."""
    logger.info(f"TagUsed: tag_name={event.tag_name}, article_id={event.article_id}, author_id={event.author_id}")
    # Simulate async operations like updating statistics
    import asyncio
    await asyncio.sleep(0.01)


async def handle_tag_removed(event: TagRemoved) -> None:
    """Handle tag removal event - could update statistics, cleanup unused tags, etc."""
    logger.info(f"TagRemoved: tag_name={event.tag_name}, article_id={event.article_id}, author_id={event.author_id}")
    # Simulate async operations like updating statistics
    import asyncio
    await asyncio.sleep(0.01)


async def handle_popular_tag_detected(event: PopularTagDetected) -> None:
    """Handle popular tag detection - could feature popular tags, adjust rankings, etc."""
    logger.info(
        f"PopularTagDetected: tag_name={event.tag_name}, usage_count={event.usage_count}, "
        f"trend_score={event.trend_score}"
    )
    # Simulate async operations like updating featured tags
    import asyncio
    await asyncio.sleep(0.01)


def register_tag_handlers() -> None:
    """Register all tag event handlers."""
    shared_event_bus.subscribe_async(TagCreated, handle_tag_created)
    shared_event_bus.subscribe_async(TagUsed, handle_tag_used)
    shared_event_bus.subscribe_async(TagRemoved, handle_tag_removed)
    shared_event_bus.subscribe_async(PopularTagDetected, handle_popular_tag_detected)