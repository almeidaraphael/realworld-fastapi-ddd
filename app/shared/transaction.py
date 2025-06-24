"""
Transaction management utilities for the service layer.

This module provides decorators and context managers to ensure
consistent transaction handling across all service methods.
"""

import functools
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any, ParamSpec, TypeVar

from app.adapters.orm.unit_of_work import AsyncUnitOfWork

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class TransactionError(Exception):
    """Exception raised when transaction management fails."""

    pass


@asynccontextmanager
async def transactional_context() -> AsyncGenerator[AsyncUnitOfWork, None]:
    """
    Async context manager for transactional operations.

    Usage:
        async with transactional_context() as uow:
            repo = SomeRepository(uow.session)
            # Perform operations
            # Transaction is automatically committed on success
            # or rolled back on exception
    """
    try:
        async with AsyncUnitOfWork() as uow:
            logger.debug("Starting transaction context")
            yield uow
            logger.debug("Transaction context completed successfully")
    except Exception as e:
        logger.error("Transaction context failed: %s", e)
        raise


def transactional(
    *,
    reraise: bool = True,
    log_errors: bool = True,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Decorator to wrap service functions in a transaction.

    This decorator automatically manages database transactions for service functions.
    The UnitOfWork is injected as the first parameter of the decorated function.

    Args:
        reraise: Whether to reraise exceptions after logging (default: True)
        log_errors: Whether to log exceptions (default: True)

    Usage:
        @transactional()
        async def create_user(uow: AsyncUnitOfWork, user_data: UserCreate) -> UserRead:
            # Function automatically runs in a transaction
            # UoW is automatically provided as first parameter
            repo = UserRepository(uow.session)
            # ... business logic
            return result

        # For functions that should not reraise errors:
        @transactional(reraise=False, log_errors=True)
        async def risky_operation(uow: AsyncUnitOfWork) -> bool:
            # Returns None on error instead of reraising
            pass
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                async with AsyncUnitOfWork() as uow:
                    logger.debug("Starting transaction for %s", func.__name__)

                    # For instance methods, inject UoW as the second parameter (after self)
                    # For functions, inject UoW as the first parameter
                    if args and hasattr(args[0], func.__name__):
                        # This is likely an instance method call
                        result = await func(args[0], uow, *args[1:], **kwargs)
                    else:
                        # This is a function call
                        result = await func(uow, *args, **kwargs)

                    logger.debug("Transaction completed successfully for %s", func.__name__)
                    return result

            except Exception as e:
                if log_errors:
                    logger.error("Transaction failed for %s: %s", func.__name__, e)

                if reraise:
                    raise

                # Return None for functions that should not reraise
                return None  # type: ignore[return-value]

        return wrapper

    return decorator


class TransactionalService:
    """
    Base class for services that provides transaction management utilities.

    Services can inherit from this class to get access to transaction
    management methods without manual decorator application.
    """

    async def _execute_in_transaction(
        self,
        operation: Callable[[AsyncUnitOfWork], Awaitable[T]],
        *,
        reraise: bool = True,
        log_errors: bool = True,
    ) -> T | None:
        """
        Execute an operation within a transaction.

        Args:
            operation: Async function that takes UoW and returns a result
            reraise: Whether to reraise exceptions
            log_errors: Whether to log exceptions

        Returns:
            Result of the operation or None if error occurred and reraise=False
        """
        try:
            async with AsyncUnitOfWork() as uow:
                logger.debug("Executing operation in transaction")
                result = await operation(uow)
                logger.debug("Transaction operation completed successfully")
                return result

        except Exception as e:
            if log_errors:
                logger.error("Transaction operation failed: %s", e)

            if reraise:
                raise

            return None

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncUnitOfWork, None]:
        """
        Context manager for manual transaction control.

        Usage:
            async with self.transaction() as uow:
                repo = SomeRepository(uow.session)
                # Perform operations
        """
        async with transactional_context() as uow:
            yield uow


# Convenience functions for backward compatibility and ease of use
async def with_transaction(operation: Callable[[AsyncUnitOfWork], Awaitable[T]]) -> T:
    """
    Execute an operation within a transaction (convenience function).

    Args:
        operation: Async function that takes UoW and returns a result

    Returns:
        Result of the operation

    Usage:
        result = await with_transaction(
            lambda uow: some_operation(uow, param1, param2)
        )
    """
    async with AsyncUnitOfWork() as uow:
        return await operation(uow)


class BulkTransactionManager:
    """
    Manager for handling bulk operations within a single transaction.

    Useful for operations that need to perform multiple related database
    operations that should all succeed or all fail together.
    """

    def __init__(self) -> None:
        self._operations: list[Callable[[AsyncUnitOfWork], Awaitable[Any]]] = []

    def add_operation(self, operation: Callable[[AsyncUnitOfWork], Awaitable[Any]]) -> None:
        """Add an operation to be executed in the bulk transaction."""
        self._operations.append(operation)

    async def execute_all(self) -> list[Any]:
        """
        Execute all registered operations in a single transaction.

        Returns:
            List of results from all operations
        """
        if not self._operations:
            return []

        async with AsyncUnitOfWork() as uow:
            logger.debug("Executing %d operations in bulk transaction", len(self._operations))
            results = []

            for i, operation in enumerate(self._operations):
                try:
                    result = await operation(uow)
                    results.append(result)
                    logger.debug("Bulk operation %d completed successfully", i + 1)
                except Exception as e:
                    logger.error("Bulk operation %d failed: %s", i + 1, e)
                    raise

            logger.debug("All bulk operations completed successfully")
            return results

    def clear(self) -> None:
        """Clear all registered operations."""
        self._operations.clear()
