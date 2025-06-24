"""
Domain exceptions for user-related operations.
"""

from app.shared.exceptions import AuthenticationError, ConflictError, NotFoundError


class UserError(Exception):
    """Base exception for all user-related errors."""


class UserAlreadyExistsError(ConflictError):
    """Raised when a user with the given username or email already exists."""


class UserNotFoundError(NotFoundError):
    """Raised when a user is not found."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when user credentials are invalid."""
