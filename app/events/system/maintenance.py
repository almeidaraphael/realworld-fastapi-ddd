"""
System-level events for data consistency and cleanup operations.
"""

from app.events.core import DomainEvent


class UserDataCleanupRequested(DomainEvent):
    """
    Event published when a user's data needs to be cleaned up (e.g., GDPR request).

    This event is triggered when users request data deletion or when compliance
    regulations require data cleanup. Handlers can use this event to schedule
    data anonymization, remove personal information, or perform complete account
    deletion as required by privacy laws.

    Args:
        user_id: The unique identifier of the user whose data needs cleanup
        username: The username of the user
        cleanup_type: The type of cleanup required ("full", "partial", "anonymize")

    Usage:
        shared_event_bus.publish(UserDataCleanupRequested(
            user_id=123,
            username="johndoe",
            cleanup_type="full"
        ))
    """

    def __init__(self, user_id: int, username: str, cleanup_type: str = "full") -> None:
        self.user_id = user_id
        self.username = username
        self.cleanup_type = cleanup_type  # "full", "partial", "anonymize"


class OrphanedDataDetected(DomainEvent):
    """
    Event published when orphaned data is detected in the system.

    This event is triggered when automated systems detect data that no longer
    has valid parent relationships (e.g., comments without articles, favorites
    for deleted articles). Handlers can use this event to schedule cleanup
    operations or investigate data integrity issues.

    Args:
        entity_type: The type of orphaned entities ("comment", "article", "favorite", etc.)
        entity_ids: List of unique identifiers for the orphaned entities
        reason: Description of why the data is considered orphaned

    Usage:
        shared_event_bus.publish(OrphanedDataDetected(
            entity_type="comment",
            entity_ids=[123, 456, 789],
            reason="Comments exist for deleted article"
        ))
    """

    def __init__(self, entity_type: str, entity_ids: list[int], reason: str) -> None:
        self.entity_type = entity_type  # "comment", "article", "favorite", etc.
        self.entity_ids = entity_ids
        self.reason = reason


class DatabaseConstraintViolation(DomainEvent):
    """
    Event published when a database constraint violation occurs.

    This event is triggered when database operations fail due to constraint
    violations such as foreign key violations, unique constraints, or check
    constraints. Handlers can use this event to log errors, alert administrators,
    or trigger data repair processes.

    Args:
        operation: The database operation that failed ("insert", "update", "delete")
        entity_type: The type of entity involved in the violation
        constraint: The name or type of constraint that was violated
        details: Additional details about the violation (optional)

    Usage:
        shared_event_bus.publish(DatabaseConstraintViolation(
            operation="insert",
            entity_type="comment",
            constraint="foreign_key_article_id",
            details="Article 123 does not exist"
        ))
    """

    def __init__(
        self, operation: str, entity_type: str, constraint: str, details: str = ""
    ) -> None:
        self.operation = operation  # "insert", "update", "delete"
        self.entity_type = entity_type
        self.constraint = constraint
        self.details = details


class BulkOperationCompleted(DomainEvent):
    """
    Event published when a bulk operation is completed.

    This event is triggered when large-scale database operations (such as
    bulk deletions, updates, or migrations) finish execution. Handlers can
    use this event to log operation results, trigger follow-up processes,
    or send completion notifications.

    Args:
        operation: The type of bulk operation performed ("delete", "update", "migrate")
        entity_type: The type of entities affected by the operation
        count: The number of entities processed
        success: Whether the operation completed successfully

    Usage:
        shared_event_bus.publish(BulkOperationCompleted(
            operation="delete",
            entity_type="comment",
            count=1500,
            success=True
        ))
    """

    def __init__(self, operation: str, entity_type: str, count: int, success: bool) -> None:
        self.operation = operation  # "delete", "update", "migrate"
        self.entity_type = entity_type
        self.count = count
        self.success = success


class RateLimitExceeded(DomainEvent):
    """
    Event published when rate limits are exceeded.

    This event is triggered when users or IP addresses exceed configured
    rate limits for various operations. Handlers can use this event to
    implement temporary blocks, send warnings, or adjust rate limiting
    policies dynamically.

    Args:
        user_id: The unique identifier of the user exceeding limits (None for anonymous)
        ip_address: The IP address associated with the rate limit violation (optional)
        operation: The operation that triggered the rate limit
            ("create_article", "add_comment", "follow_user")
        limit_type: The type of rate limit exceeded ("hourly", "daily", "per_minute")

    Usage:
        shared_event_bus.publish(RateLimitExceeded(
            user_id=123,
            ip_address="192.168.1.1",
            operation="create_article",
            limit_type="hourly"
        ))
    """

    def __init__(
        self, user_id: int | None, ip_address: str | None, operation: str, limit_type: str
    ) -> None:
        self.user_id = user_id
        self.ip_address = ip_address
        self.operation = operation  # "create_article", "add_comment", "follow_user"
        self.limit_type = limit_type  # "hourly", "daily", "per_minute"
