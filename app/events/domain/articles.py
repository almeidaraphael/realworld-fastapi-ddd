"""
Domain events for the articles domain.
"""

from app.events.core import DomainEvent


class ArticleCreated(DomainEvent):
    """
    Event published when an article is created.

    This event is triggered when a new article is successfully created and saved
    to the database. Handlers can use this event to trigger notifications to
    followers, index the article for search, or update recommendation engines.

    Args:
        article_id: The unique identifier of the created article
        author_id: The unique identifier of the article's author

    Usage:
        shared_event_bus.publish(ArticleCreated(article_id=123, author_id=456))
    """

    def __init__(self, article_id: int, author_id: int) -> None:
        self.article_id = article_id
        self.author_id = author_id


class ArticleUpdated(DomainEvent):
    """
    Event published when an article is updated.

    This event is triggered when an article's content, title, description, or tags
    are modified. Handlers can use this event to reindex for search, track edit
    history, or update cached content.

    Args:
        article_id: The unique identifier of the updated article
        author_id: The unique identifier of the article's author
        updated_fields: List of field names that were modified (e.g., ["title", "body"])

    Usage:
        shared_event_bus.publish(ArticleUpdated(
            article_id=123,
            author_id=456,
            updated_fields=["title", "description"]
        ))
    """

    def __init__(self, article_id: int, author_id: int, updated_fields: list[str]) -> None:
        self.article_id = article_id
        self.author_id = author_id
        self.updated_fields = updated_fields


class ArticleDeleted(DomainEvent):
    """
    Event published when an article is deleted.

    This event is triggered when an article is permanently removed from the system.
    Handlers can use this event to clean up related data (comments, favorites),
    remove from search indexes, or trigger cleanup processes.

    Args:
        article_id: The unique identifier of the deleted article
        author_id: The unique identifier of the article's author

    Usage:
        shared_event_bus.publish(ArticleDeleted(article_id=123, author_id=456))
    """

    def __init__(self, article_id: int, author_id: int) -> None:
        self.article_id = article_id
        self.author_id = author_id


class ArticleFavorited(DomainEvent):
    """
    Event published when an article is favorited by a user.

    This event is triggered when a user adds an article to their favorites.
    Handlers can use this event to update recommendation algorithms, notify
    the article author, or update analytics.

    Args:
        article_id: The unique identifier of the favorited article
        user_id: The unique identifier of the user who favorited the article

    Usage:
        shared_event_bus.publish(ArticleFavorited(article_id=123, user_id=789))
    """

    def __init__(self, article_id: int, user_id: int) -> None:
        self.article_id = article_id
        self.user_id = user_id


class ArticleUnfavorited(DomainEvent):
    """
    Event published when an article is unfavorited by a user.

    This event is triggered when a user removes an article from their favorites.
    Handlers can use this event to update recommendation algorithms or analytics.

    Args:
        article_id: The unique identifier of the unfavorited article
        user_id: The unique identifier of the user who unfavorited the article

    Usage:
        shared_event_bus.publish(ArticleUnfavorited(article_id=123, user_id=789))
    """

    def __init__(self, article_id: int, user_id: int) -> None:
        self.article_id = article_id
        self.user_id = user_id
