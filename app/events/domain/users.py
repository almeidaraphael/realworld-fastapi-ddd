"""
Domain events for the users domain.
"""

from app.events.core import DomainEvent


class UserRegistered(DomainEvent):
    """
    Event published when a new user registers.

    This event is triggered when a user successfully completes the registration
    process and their account is created. Handlers can use this event to send
    welcome emails, initialize user preferences, or set up default settings.

    Args:
        user_id: The unique identifier of the newly registered user
        username: The username chosen by the user
        email: The email address of the user

    Usage:
        shared_event_bus.publish(UserRegistered(
            user_id=123,
            username="johndoe",
            email="john@example.com"
        ))
    """

    def __init__(self, user_id: int, username: str, email: str) -> None:
        self.user_id = user_id
        self.username = username
        self.email = email


class UserLoggedIn(DomainEvent):
    """
    Event published when a user successfully logs in.

    This event is triggered when a user provides valid credentials and is
    authenticated. Handlers can use this event for security monitoring,
    login analytics, or updating last login timestamps.

    Args:
        user_id: The unique identifier of the user who logged in
        username: The username of the user
        email: The email address of the user

    Usage:
        shared_event_bus.publish(UserLoggedIn(
            user_id=123,
            username="johndoe",
            email="john@example.com"
        ))
    """

    def __init__(self, user_id: int, username: str, email: str) -> None:
        self.user_id = user_id
        self.username = username
        self.email = email


class UserProfileUpdated(DomainEvent):
    """
    Event published when a user updates their profile.

    This event is triggered when a user modifies their profile information
    such as bio, image, or other settings. Handlers can use this event to
    sync with external systems or trigger profile validation.

    Args:
        user_id: The unique identifier of the user who updated their profile
        username: The username of the user
        updated_fields: List of field names that were modified (e.g., ["bio", "image"])

    Usage:
        shared_event_bus.publish(UserProfileUpdated(
            user_id=123,
            username="johndoe",
            updated_fields=["bio", "image"]
        ))
    """

    def __init__(self, user_id: int, username: str, updated_fields: list[str]) -> None:
        self.user_id = user_id
        self.username = username
        self.updated_fields = updated_fields


class UserFollowed(DomainEvent):
    """
    Event published when a user follows another user.

    This event is triggered when a follow relationship is established between
    two users. Handlers can use this event to update personalized feeds,
    send notifications, or update recommendation algorithms.

    Args:
        follower_id: The unique identifier of the user who is following
        followee_id: The unique identifier of the user being followed

    Usage:
        shared_event_bus.publish(UserFollowed(
            follower_id=123,
            followee_id=456
        ))
    """

    def __init__(self, follower_id: int, followee_id: int) -> None:
        self.follower_id = follower_id
        self.followee_id = followee_id


class UserUnfollowed(DomainEvent):
    """
    Event published when a user unfollows another user.

    This event is triggered when a follow relationship is removed between
    two users. Handlers can use this event to update personalized feeds
    or recommendation algorithms.

    Args:
        follower_id: The unique identifier of the user who is unfollowing
        followee_id: The unique identifier of the user being unfollowed

    Usage:
        shared_event_bus.publish(UserUnfollowed(
            follower_id=123,
            followee_id=456
        ))
    """

    def __init__(self, follower_id: int, followee_id: int) -> None:
        self.follower_id = follower_id
        self.followee_id = followee_id
