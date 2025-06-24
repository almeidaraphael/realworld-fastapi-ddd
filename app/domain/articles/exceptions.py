"""
Domain exceptions for article-related operations.

Contains specific exceptions that can occur during article operations,
providing better error handling and more informative error messages.
"""


class ArticleError(Exception):
    """Base exception for all article-related errors."""


class ArticleNotFoundError(ArticleError):
    """Raised when an article cannot be found."""


class ArticleSlugConflictError(ArticleError):
    """Raised when an article slug already exists."""


class ArticlePermissionError(ArticleError):
    """Raised when a user lacks permission to perform an article operation."""


class InvalidArticleDataError(ArticleError):
    """Raised when article data is invalid or incomplete."""
