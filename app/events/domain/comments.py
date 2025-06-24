"""
Domain events for the comments domain.
"""

from app.events.core import DomainEvent


class ArticleCommentAdded(DomainEvent):
    """
    Event published when a comment is added to an article.

    This event is triggered when a new comment is successfully created and
    associated with an article. Handlers can use this event to notify the
    article author, moderate content, or update engagement metrics.

    Args:
        article_id: The unique identifier of the article that received the comment
        comment_id: The unique identifier of the new comment
        author_id: The unique identifier of the comment's author

    Usage:
        shared_event_bus.publish(ArticleCommentAdded(
            article_id=123,
            comment_id=456,
            author_id=789
        ))
    """

    def __init__(self, article_id: int, comment_id: int, author_id: int) -> None:
        self.article_id = article_id
        self.comment_id = comment_id
        self.author_id = author_id


class CommentDeleted(DomainEvent):
    """
    Event published when a comment is deleted.

    This event is triggered when a comment is permanently removed from an article.
    Handlers can use this event to update thread counts, log moderation actions,
    or clean up related data.

    Args:
        comment_id: The unique identifier of the deleted comment
        article_id: The unique identifier of the article the comment belonged to
        author_id: The unique identifier of the comment's author

    Usage:
        shared_event_bus.publish(CommentDeleted(
            comment_id=456,
            article_id=123,
            author_id=789
        ))
    """

    def __init__(self, comment_id: int, article_id: int, author_id: int) -> None:
        self.comment_id = comment_id
        self.article_id = article_id
        self.author_id = author_id
