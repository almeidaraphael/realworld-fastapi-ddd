"""
Security-related events for user authentication and access control.
"""

from app.events.core import DomainEvent


class UserLoginAttempted(DomainEvent):
    """
    Event published when a user attempts to log in (success or failure).

    This event is triggered for every login attempt, whether successful or not.
    Handlers can use this event for security monitoring, fraud detection,
    rate limiting, and audit logging.

    Args:
        email: The email address used in the login attempt
        success: True if login was successful, False if it failed
        ip_address: The IP address of the login attempt (optional)

    Usage:
        # Successful login
        shared_event_bus.publish(UserLoginAttempted(
            email="user@example.com",
            success=True,
            ip_address="192.168.1.1"
        ))

        # Failed login
        shared_event_bus.publish(UserLoginAttempted(
            email="user@example.com",
            success=False,
            ip_address="192.168.1.1"
        ))
    """

    def __init__(self, email: str, success: bool, ip_address: str | None = None) -> None:
        self.email = email
        self.success = success
        self.ip_address = ip_address


class UserPasswordChanged(DomainEvent):
    """
    Event published when a user changes their password.

    This event is triggered when a user successfully updates their password.
    Handlers can use this event for security notifications, audit logging,
    or triggering additional security measures.

    Args:
        user_id: The unique identifier of the user who changed their password
        username: The username of the user

    Usage:
        shared_event_bus.publish(UserPasswordChanged(
            user_id=123,
            username="johndoe"
        ))
    """

    def __init__(self, user_id: int, username: str) -> None:
        self.user_id = user_id
        self.username = username


class UserAccountLocked(DomainEvent):
    """
    Event published when a user account is locked due to too many failed attempts.

    This event is triggered when security measures automatically lock a user
    account due to suspicious activity or too many failed login attempts.
    Handlers can use this event to send security alerts or notify administrators.

    Args:
        user_id: The unique identifier of the locked user account
        username: The username of the locked account
        email: The email address of the locked account

    Usage:
        shared_event_bus.publish(UserAccountLocked(
            user_id=123,
            username="johndoe",
            email="john@example.com"
        ))
    """

    def __init__(self, user_id: int, username: str, email: str) -> None:
        self.user_id = user_id
        self.username = username
        self.email = email


class SuspiciousLoginActivity(DomainEvent):
    """
    Event published when suspicious login activity is detected.

    This event is triggered when automated systems detect potentially
    fraudulent or suspicious login patterns. Handlers can use this event
    to implement additional security measures or send alerts.

    Args:
        email: The email address associated with the suspicious activity
        ip_address: The IP address of the suspicious activity (optional)
        reason: Description of why the activity was flagged as suspicious

    Usage:
        shared_event_bus.publish(SuspiciousLoginActivity(
            email="user@example.com",
            ip_address="192.168.1.1",
            reason="Multiple failed attempts from unknown location"
        ))
    """

    def __init__(self, email: str, ip_address: str | None = None, reason: str = "") -> None:
        self.email = email
        self.ip_address = ip_address
        self.reason = reason
