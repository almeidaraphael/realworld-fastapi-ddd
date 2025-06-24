"""
Tag-related domain events.
"""

from app.events.core import DomainEvent


class TagCreated(DomainEvent):
    """
    Event published when a new tag is first used.

    This event is triggered when a tag is created for the first time in the system,
    typically when an author adds a new tag to an article. Handlers can use this
    event to initialize tag metadata, update search indexes, or track tag creation patterns.

    Args:
        tag_name: The name of the newly created tag
        article_id: The unique identifier of the article where the tag was first used
        author_id: The unique identifier of the user who created the tag

    Usage:
        shared_event_bus.publish(TagCreated(
            tag_name="machine-learning",
            article_id=123,
            author_id=456
        ))
    """

    def __init__(self, tag_name: str, article_id: int, author_id: int) -> None:
        self.tag_name = tag_name
        self.article_id = article_id
        self.author_id = author_id


class TagUsed(DomainEvent):
    """
    Event published when an existing tag is used in an article.

    This event is triggered when an author adds an existing tag to their article.
    Handlers can use this event to update tag usage statistics, improve
    recommendation algorithms, or track content categorization patterns.

    Args:
        tag_name: The name of the tag being used
        article_id: The unique identifier of the article using the tag
        author_id: The unique identifier of the user using the tag

    Usage:
        shared_event_bus.publish(TagUsed(
            tag_name="python",
            article_id=123,
            author_id=456
        ))
    """

    def __init__(self, tag_name: str, article_id: int, author_id: int) -> None:
        self.tag_name = tag_name
        self.article_id = article_id
        self.author_id = author_id


class TagRemoved(DomainEvent):
    """
    Event published when a tag is removed from an article.

    This event is triggered when an author removes a tag from their article.
    Handlers can use this event to update tag usage statistics, clean up
    unused tags, or adjust content categorization.

    Args:
        tag_name: The name of the tag being removed
        article_id: The unique identifier of the article the tag was removed from
        author_id: The unique identifier of the user removing the tag

    Usage:
        shared_event_bus.publish(TagRemoved(
            tag_name="deprecated",
            article_id=123,
            author_id=456
        ))
    """

    def __init__(self, tag_name: str, article_id: int, author_id: int) -> None:
        self.tag_name = tag_name
        self.article_id = article_id
        self.author_id = author_id


class PopularTagDetected(DomainEvent):
    """
    Event published when a tag becomes trending/popular.

    This event is triggered when automated systems detect that a tag has become
    popular or trending based on usage patterns and metrics. Handlers can use
    this event to feature popular tags, adjust search rankings, or send
    notifications about trending topics.

    Args:
        tag_name: The name of the tag that became popular
        usage_count: The current number of times this tag has been used
        trend_score: A calculated score indicating the trend strength (0.0-1.0)

    Usage:
        shared_event_bus.publish(PopularTagDetected(
            tag_name="ai",
            usage_count=150,
            trend_score=0.85
        ))
    """

    def __init__(self, tag_name: str, usage_count: int, trend_score: float) -> None:
        self.tag_name = tag_name
        self.usage_count = usage_count
        self.trend_score = trend_score
