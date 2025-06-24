"""
Cross-domain event handlers that react to events from other domains.
Demonstrates how events enable loose coupling between domains.
"""

import logging

from app.events import (
    ArticleCommentAdded,
    ArticleCreated,
    ArticleDeleted,
    CommentDeleted,
    UserFollowed,
    UserRegistered,
    UserUnfollowed,
    shared_event_bus,
)

logger = logging.getLogger(__name__)


def handle_user_registered_for_recommendations(event: UserRegistered) -> None:
    """When a user registers, initialize their recommendation engine."""
    logger.info(
        f"Recommendations: Initializing for new user {event.username} (ID: {event.user_id})"
    )


def handle_article_created_for_notifications(event: ArticleCreated) -> None:
    """When an article is created, notify followers of the author."""
    logger.info(f"Notifications: New article {event.article_id} by author {event.author_id}")


def handle_comment_added_for_notifications(event: ArticleCommentAdded) -> None:
    """When a comment is added, notify the article author."""
    logger.info(
        f"Notifications: New comment on article {event.article_id} by user {event.author_id}"
    )


def handle_follow_for_feed_updates(event: UserFollowed) -> None:
    """When a user follows another, update their personalized feed."""
    logger.info(f"Feed: User {event.follower_id} now following {event.followee_id} - updating feed")


def handle_unfollow_for_feed_updates(event: UserUnfollowed) -> None:
    """When a user unfollows another, update their personalized feed."""
    logger.info(f"Feed: User {event.follower_id} unfollowed {event.followee_id} - updating feed")


def handle_article_deleted_for_cleanup(event: ArticleDeleted) -> None:
    """When an article is deleted, clean up related data."""
    logger.info(
        f"Cleanup: Article {event.article_id} deleted - cleaning up comments, favorites, etc."
    )


def handle_comment_deleted_for_analytics(event: CommentDeleted) -> None:
    """When a comment is deleted, update engagement analytics."""
    logger.info(f"Analytics: Comment {event.comment_id} deleted from article {event.article_id}")


def register_cross_domain_handlers() -> None:
    """Register all cross-domain event handlers."""
    shared_event_bus.subscribe(UserRegistered, handle_user_registered_for_recommendations)
    shared_event_bus.subscribe(ArticleCreated, handle_article_created_for_notifications)
    shared_event_bus.subscribe(ArticleCommentAdded, handle_comment_added_for_notifications)
    shared_event_bus.subscribe(UserFollowed, handle_follow_for_feed_updates)
    shared_event_bus.subscribe(UserUnfollowed, handle_unfollow_for_feed_updates)
    shared_event_bus.subscribe(ArticleDeleted, handle_article_deleted_for_cleanup)
    shared_event_bus.subscribe(CommentDeleted, handle_comment_deleted_for_analytics)
