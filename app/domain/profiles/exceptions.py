"""
Domain exceptions for profile-related operations.
"""

from app.shared.exceptions import DomainError, NotFoundError, ValidationError


class ProfileError(DomainError):
    """Base exception for all profile-related errors."""


class ProfileNotFoundError(NotFoundError):
    """Raised when a profile is not found."""


class CannotFollowYourselfError(ValidationError):
    """Raised when a user tries to follow themselves."""

    def __init__(self, message: str = "Cannot follow yourself") -> None:
        super().__init__(message, error_code="CANNOT_FOLLOW_SELF")


class UserOrFollowerIdMissingError(ValidationError):
    """Raised when a user or follower has no id."""
