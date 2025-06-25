"""
Additional essential domain events for comprehensive event coverage.

These events cover important business scenarios that weren't captured
in the basic CRUD operations.
"""

from app.events.core import DomainEvent


class UserLoginAttempted(DomainEvent):
    """
    Event published when a user attempts to log in (success or failure).
    
    This event is useful for security monitoring, rate limiting,
    and login analytics.
    """
    
    def __init__(self, email: str, success: bool, ip_address: str | None = None) -> None:
        self.email = email
        self.success = success
        self.ip_address = ip_address


class UserPasswordChanged(DomainEvent):
    """
    Event published when a user changes their password.
    
    This event is useful for security notifications and auditing.
    """
    
    def __init__(self, user_id: int, username: str) -> None:
        self.user_id = user_id
        self.username = username


class ArticleViewIncremented(DomainEvent):
    """
    Event published when an article is viewed.
    
    This event is triggered every time an article is accessed,
    useful for analytics and recommendation systems.
    """
    
    def __init__(self, article_id: int, viewer_id: int | None = None) -> None:
        self.article_id = article_id
        self.viewer_id = viewer_id


class UserAccountDeactivated(DomainEvent):
    """
    Event published when a user account is deactivated.
    
    This event triggers cleanup processes, notifications,
    and system-wide user removal.
    """
    
    def __init__(self, user_id: int, username: str, reason: str | None = None) -> None:
        self.user_id = user_id
        self.username = username
        self.reason = reason


class ArticleContentModerated(DomainEvent):
    """
    Event published when article content is flagged or moderated.
    
    This event is useful for content moderation workflows
    and compliance tracking.
    """
    
    def __init__(self, article_id: int, author_id: int, moderation_action: str, reason: str) -> None:
        self.article_id = article_id
        self.author_id = author_id
        self.moderation_action = moderation_action  # "flagged", "hidden", "approved"
        self.reason = reason