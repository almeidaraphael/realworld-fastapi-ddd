"""
Domain exceptions for tag-related operations.
"""

from app.shared.exceptions import NotFoundError


class TagError(Exception):
    """Base exception for all tag-related errors."""


class TagNotFoundError(NotFoundError):
    """Raised when a tag is not found."""
