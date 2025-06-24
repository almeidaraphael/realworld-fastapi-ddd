"""
Domain exceptions for article-related operations.

Contains specific exceptions that can occur during article operations,
providing better error handling and more informative error messages.
"""

from app.shared.exceptions import ConflictError, NotFoundError, PermissionError, ValidationError


class ArticleError(Exception):
    """Base exception for all article-related errors."""


class ArticleNotFoundError(NotFoundError):
    """Raised when an article cannot be found."""


class ArticleSlugConflictError(ConflictError):
    """Raised when an article slug already exists."""


class ArticlePermissionError(PermissionError):
    """Raised when a user lacks permission to perform an article operation."""


class InvalidArticleDataError(ValidationError):
    """Raised when article data is invalid or incomplete."""
