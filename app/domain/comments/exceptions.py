"""
Domain exceptions for comment-related operations.
"""

from app.shared.exceptions import DomainError, NotFoundError, PermissionError


class CommentError(DomainError):
    """Base exception for all comment-related errors."""


class CommentNotFoundError(NotFoundError):
    """Raised when a comment is not found."""


class CommentPermissionError(PermissionError):
    """Raised when a user doesn't have permission to delete a comment."""
