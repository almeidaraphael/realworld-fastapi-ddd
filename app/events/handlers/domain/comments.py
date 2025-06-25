"""
Event handlers for comment domain events.
Handles comment lifecycle events including creation and deletion.
"""

import asyncio
import logging

from app.events import ArticleCommentAdded, CommentDeleted, shared_event_bus

logger = logging.getLogger(__name__)


async def handle_article_comment_added(event: ArticleCommentAdded) -> None:
    """Handle comment addition event - could notify article author, moderate content, etc."""
    logger.info(
        f"ArticleCommentAdded: article_id={event.article_id}, "
        f"comment_id={event.comment_id}, author_id={event.author_id}"
    )
    # Simulate async work (e.g., notifying article author, content moderation)
    await asyncio.sleep(0.01)


async def handle_comment_deleted(event: CommentDeleted) -> None:
    """Handle comment deletion event - could update thread counts, log moderation, etc."""
    logger.info(
        f"CommentDeleted: comment_id={event.comment_id}, "
        f"article_id={event.article_id}, author_id={event.author_id}"
    )
    # Simulate async work (e.g., updating analytics, cleanup operations)
    await asyncio.sleep(0.01)


def register_comment_handlers() -> None:
    """Register all comment event handlers."""
    shared_event_bus.subscribe_async(ArticleCommentAdded, handle_article_comment_added)
    shared_event_bus.subscribe_async(CommentDeleted, handle_comment_deleted)
