"""
Event handlers for article domain events.
Includes both sync and async handlers for article lifecycle events.
"""

import asyncio
import logging

from app.events import (
    ArticleCommentAdded,
    ArticleCreated,
    ArticleDeleted,
    ArticleFavorited,
    ArticleUnfavorited,
    ArticleUpdated,
    shared_event_bus,
)

logger = logging.getLogger(__name__)


# Sync handlers
def handle_article_created(event: ArticleCreated) -> None:
    """Handle article creation event - could index for search, notify followers, etc."""
    logger.info(f"ArticleCreated: article_id={event.article_id}, author_id={event.author_id}")


def handle_article_updated(event: ArticleUpdated) -> None:
    """Handle article update event - could reindex for search, track edit history, etc."""
    logger.info(
        f"ArticleUpdated: article_id={event.article_id}, author_id={event.author_id}, "
        f"fields={event.updated_fields}"
    )


def handle_article_deleted(event: ArticleDeleted) -> None:
    """Handle article deletion event - could remove from search index, cleanup, etc."""
    logger.info(f"ArticleDeleted: article_id={event.article_id}, author_id={event.author_id}")


def handle_article_favorited(event: ArticleFavorited) -> None:
    """Handle article favorited event - could update recommendations, notify author, etc."""
    logger.info(f"ArticleFavorited: article_id={event.article_id}, user_id={event.user_id}")


def handle_article_unfavorited(event: ArticleUnfavorited) -> None:
    """Handle article unfavorited event - could update recommendations, etc."""
    logger.info(f"ArticleUnfavorited: article_id={event.article_id}, user_id={event.user_id}")


# Async handlers
async def async_handle_article_created(event: ArticleCreated) -> None:
    """Async handler for article creation - could send notifications, etc."""
    logger.info(f"Async: Article {event.article_id} created by user {event.author_id}")
    # Simulate async work (e.g., sending email, updating external systems)
    await asyncio.sleep(0.1)
    logger.info(f"Async processing complete for article {event.article_id}")


async def async_handle_article_favorited(event: ArticleFavorited) -> None:
    """Async handler for article favoriting - could update recommendation engines."""
    logger.info(f"Async: Article {event.article_id} favorited by user {event.user_id}")
    # Simulate async work (e.g., updating recommendation algorithms)
    await asyncio.sleep(0.05)


async def async_handle_comment_added(event: ArticleCommentAdded) -> None:
    """Async handler for comment addition - could trigger notifications."""
    logger.info(
        f"Async: Comment {event.comment_id} added to article {event.article_id} "
        f"by user {event.author_id}"
    )
    # Simulate async work (e.g., notifying article author)
    await asyncio.sleep(0.02)


def register_article_handlers() -> None:
    """Register all article event handlers."""
    # Sync handlers
    shared_event_bus.subscribe(ArticleCreated, handle_article_created)
    shared_event_bus.subscribe(ArticleUpdated, handle_article_updated)
    shared_event_bus.subscribe(ArticleDeleted, handle_article_deleted)
    shared_event_bus.subscribe(ArticleFavorited, handle_article_favorited)
    shared_event_bus.subscribe(ArticleUnfavorited, handle_article_unfavorited)

    # Async handlers
    shared_event_bus.subscribe_async(ArticleCreated, async_handle_article_created)
    shared_event_bus.subscribe_async(ArticleFavorited, async_handle_article_favorited)
    shared_event_bus.subscribe_async(ArticleCommentAdded, async_handle_comment_added)
