"""
Domain exceptions for profile-related operations.
"""

from app.shared.exceptions import NotFoundError, ValidationError


class ProfileError(Exception):
    """Base exception for all profile-related errors."""


class ProfileNotFoundError(NotFoundError):
    """Raised when a profile is not found."""


class CannotFollowYourselfError(ValidationError):
    """Raised when a user tries to follow themselves."""


class UserOrFollowerIdMissingError(ValidationError):
    """Raised when a user or follower has no id."""
