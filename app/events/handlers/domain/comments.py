"""
Event handlers for comment domain events.
Handles comment lifecycle events including creation and deletion.
"""

import logging

from app.events import ArticleCommentAdded, CommentDeleted, shared_event_bus

logger = logging.getLogger(__name__)


def handle_article_comment_added(event: ArticleCommentAdded) -> None:
    """Handle comment addition event - could notify article author, moderate content, etc."""
    logger.info(
        f"ArticleCommentAdded: article_id={event.article_id}, "
        f"comment_id={event.comment_id}, author_id={event.author_id}"
    )


def handle_comment_deleted(event: CommentDeleted) -> None:
    """Handle comment deletion event - could update thread counts, log moderation, etc."""
    logger.info(
        f"CommentDeleted: comment_id={event.comment_id}, "
        f"article_id={event.article_id}, author_id={event.author_id}"
    )


def register_comment_handlers() -> None:
    """Register all comment event handlers."""
    shared_event_bus.subscribe(ArticleCommentAdded, handle_article_comment_added)
    shared_event_bus.subscribe(CommentDeleted, handle_comment_deleted)
