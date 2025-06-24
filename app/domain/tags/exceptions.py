"""
Domain exceptions for tag-related operations.
"""

from app.shared.exceptions import DomainError, NotFoundError


class TagError(DomainError):
    """Base exception for all tag-related errors."""


class TagNotFoundError(NotFoundError):
    """Raised when a tag is not found."""
