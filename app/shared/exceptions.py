"""
Shared exception handling infrastructure for the FastAPI RealWorld application.

This module provides base exception classes and utilities for consistent error handling
across all domains and proper translation to HTTP responses in the API layer.
"""

from typing import Any, Callable

from fastapi import HTTPException, status


class DomainError(Exception):
    """
    Base exception for all domain-specific errors.

    All domain exceptions should inherit from this base class to ensure
    consistent error handling and HTTP status code mapping.
    """

    def __init__(self, message: str, error_code: str | None = None) -> None:
        """
        Initialize domain error.

        Args:
            message: Human-readable error message
            error_code: Optional error code for client identification
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code if error_code is not None else self.__class__.__name__


class NotFoundError(DomainError):
    """Base exception for resource not found errors."""

    pass


class PermissionError(DomainError):
    """Base exception for permission/authorization errors."""

    pass


class ConflictError(DomainError):
    """Base exception for resource conflict errors."""

    pass


class ValidationError(DomainError):
    """Base exception for data validation errors."""

    pass


class AuthenticationError(DomainError):
    """Base exception for authentication errors."""

    pass


# HTTP status code mapping for domain exceptions
EXCEPTION_TO_STATUS_CODE: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    PermissionError: status.HTTP_403_FORBIDDEN,
    ConflictError: status.HTTP_409_CONFLICT,
    ValidationError: status.HTTP_400_BAD_REQUEST,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
}


def get_http_status_code(exception: DomainError) -> int:
    """
    Get the appropriate HTTP status code for a domain exception.

    Args:
        exception: The domain exception instance

    Returns:
        HTTP status code for the exception type
    """
    for exc_type, status_code in EXCEPTION_TO_STATUS_CODE.items():
        if isinstance(exception, exc_type):
            return status_code

    # Default to 500 for unknown domain errors
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def translate_domain_error_to_http(exception: DomainError) -> HTTPException:
    """
    Translate a domain exception to an HTTPException.

    Args:
        exception: The domain exception to translate

    Returns:
        HTTPException with appropriate status code and detail
    """
    status_code = get_http_status_code(exception)

    # Include error code in detail if available
    detail = exception.message
    if hasattr(exception, "error_code") and exception.error_code:
        detail = f"{exception.error_code}: {detail}"

    return HTTPException(status_code=status_code, detail=detail)


def handle_domain_error(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to automatically handle domain errors in API endpoints.

    This decorator catches DomainError exceptions and translates them
    to appropriate HTTPExceptions with consistent status codes.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except DomainError as exc:
            raise translate_domain_error_to_http(exc) from exc

    # For async functions
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except DomainError as exc:
            raise translate_domain_error_to_http(exc) from exc

    import asyncio

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return wrapper
