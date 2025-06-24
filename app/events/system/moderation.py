"""
Content moderation events for articles and comments.
"""

from app.events.core import DomainEvent


class ContentFlagged(DomainEvent):
    """
    Event published when content is flagged for moderation.

    This event is triggered when users report content as inappropriate, spam,
    or violating community guidelines. Handlers can use this event to queue
    content for manual review, implement automated moderation rules, or track
    reporting patterns.

    Args:
        content_type: The type of content being flagged ("article" or "comment")
        content_id: The unique identifier of the flagged content
        reason: The reason provided for flagging the content
        reporter_id: The unique identifier of the user reporting the content
            (None for anonymous reports)

    Usage:
        shared_event_bus.publish(ContentFlagged(
            content_type="article",
            content_id=123,
            reason="Spam content",
            reporter_id=456
        ))
    """

    def __init__(
        self, content_type: str, content_id: int, reason: str, reporter_id: int | None = None
    ) -> None:
        self.content_type = content_type  # "article" or "comment"
        self.content_id = content_id
        self.reason = reason
        self.reporter_id = reporter_id


class ContentApproved(DomainEvent):
    """
    Event published when flagged content is approved.

    This event is triggered when a moderator reviews flagged content and
    determines it does not violate community guidelines. Handlers can use
    this event to remove moderation flags, notify reporters of the decision,
    or update content moderation statistics.

    Args:
        content_type: The type of content being approved ("article" or "comment")
        content_id: The unique identifier of the approved content
        moderator_id: The unique identifier of the moderator who approved the content

    Usage:
        shared_event_bus.publish(ContentApproved(
            content_type="article",
            content_id=123,
            moderator_id=789
        ))
    """

    def __init__(self, content_type: str, content_id: int, moderator_id: int) -> None:
        self.content_type = content_type
        self.content_id = content_id
        self.moderator_id = moderator_id


class ContentRemoved(DomainEvent):
    """
    Event published when content is removed due to moderation.

    This event is triggered when a moderator determines that content violates
    community guidelines and removes it from the platform. Handlers can use
    this event to notify content authors, update moderation logs, or implement
    additional penalties.

    Args:
        content_type: The type of content being removed ("article" or "comment")
        content_id: The unique identifier of the removed content
        reason: The reason for content removal
        moderator_id: The unique identifier of the moderator who removed the content

    Usage:
        shared_event_bus.publish(ContentRemoved(
            content_type="comment",
            content_id=456,
            reason="Harassment",
            moderator_id=789
        ))
    """

    def __init__(self, content_type: str, content_id: int, reason: str, moderator_id: int) -> None:
        self.content_type = content_type
        self.content_id = content_id
        self.reason = reason
        self.moderator_id = moderator_id


class SpamDetected(DomainEvent):
    """
    Event published when spam content is automatically detected.

    This event is triggered when automated systems detect content that appears
    to be spam based on various signals and patterns. Handlers can use this
    event to automatically flag content for review, implement immediate
    restrictions, or train spam detection models.

    Args:
        content_type: The type of content detected as spam ("article" or "comment")
        content_id: The unique identifier of the spam content
        author_id: The unique identifier of the content author
        confidence: The confidence score of the spam detection (0.0 to 1.0)

    Usage:
        shared_event_bus.publish(SpamDetected(
            content_type="article",
            content_id=123,
            author_id=456,
            confidence=0.95
        ))
    """

    def __init__(
        self, content_type: str, content_id: int, author_id: int, confidence: float
    ) -> None:
        self.content_type = content_type
        self.content_id = content_id
        self.author_id = author_id
        self.confidence = confidence  # 0.0 to 1.0
