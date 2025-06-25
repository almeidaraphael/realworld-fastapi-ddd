"""
Tests for transaction management utilities.

Tests the transaction decorators, context managers, and service base classes
to ensure proper transaction handling and error management.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.shared.transaction import (
    BulkTransactionManager,
    TransactionalService,
    transactional,
    transactional_context,
    with_transaction,
)


class TestTransactionalContext:
    """Test the transactional_context context manager."""

    async def test_transactional_context_successful_completion(self) -> None:
        """
        GIVEN a transactional context manager
        WHEN used successfully without exceptions
        THEN it should yield a UoW instance and commit the transaction
        """
        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            async with transactional_context() as uow:
                assert uow is mock_uow

            mock_uow_class.return_value.__aenter__.assert_awaited_once()
            mock_uow_class.return_value.__aexit__.assert_awaited_once_with(None, None, None)

    async def test_transactional_context_with_exception(self) -> None:
        """
        GIVEN a transactional context manager
        WHEN an exception occurs within the context
        THEN it should propagate the exception and rollback the transaction
        """
        test_exception = ValueError("Test error")

        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            with pytest.raises(ValueError, match="Test error"):
                async with transactional_context():
                    raise test_exception

            mock_uow_class.return_value.__aenter__.assert_awaited_once()
            # Check that __aexit__ was called with exception info
            mock_uow_class.return_value.__aexit__.assert_awaited_once()


class TestTransactionalDecorator:
    """Test the transactional decorator."""

    async def test_transactional_decorator_success(self) -> None:
        """
        GIVEN a function decorated with @transactional()
        WHEN the function executes successfully
        THEN it should receive a UoW as first parameter and commit the transaction
        """
        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            @transactional()
            async def test_function(uow: AsyncUnitOfWork, value: str) -> str:
                assert uow is mock_uow
                return f"processed: {value}"

            result = await test_function("test_value")

            assert result == "processed: test_value"
            mock_uow_class.return_value.__aenter__.assert_awaited_once()
            mock_uow_class.return_value.__aexit__.assert_awaited_once_with(None, None, None)

    async def test_transactional_decorator_with_exception_reraise_true(self) -> None:
        """
        GIVEN a function decorated with @transactional(reraise=True)
        WHEN the function raises an exception
        THEN it should reraise the exception and rollback the transaction
        """
        test_exception = ValueError("Test error")

        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            @transactional(reraise=True)
            async def failing_function(uow: AsyncUnitOfWork) -> str:
                raise test_exception

            with pytest.raises(ValueError, match="Test error"):
                await failing_function()

            mock_uow_class.return_value.__aenter__.assert_awaited_once()

    async def test_transactional_decorator_with_exception_reraise_false(self) -> None:
        """
        GIVEN a function decorated with @transactional(reraise=False)
        WHEN the function raises an exception
        THEN it should return None and rollback the transaction
        """
        test_exception = ValueError("Test error")

        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            @transactional(reraise=False)
            async def failing_function(uow: AsyncUnitOfWork) -> str:
                raise test_exception

            result = await failing_function()

            assert result is None
            mock_uow_class.return_value.__aenter__.assert_awaited_once()

    async def test_transactional_decorator_preserves_function_metadata(self) -> None:
        """
        GIVEN a function decorated with @transactional()
        WHEN checking the decorated function metadata
        THEN it should preserve the original function's name and docstring
        """

        @transactional()
        async def original_function(uow: AsyncUnitOfWork) -> str:
            """Original function docstring."""
            return "result"

        assert original_function.__name__ == "original_function"
        assert original_function.__doc__ == "Original function docstring."


class TestTransactionalService:
    """Test the TransactionalService base class."""

    async def test_execute_in_transaction_success(self) -> None:
        """
        GIVEN a TransactionalService instance
        WHEN calling _execute_in_transaction with a successful operation
        THEN it should execute the operation and return the result
        """
        service = TransactionalService()

        async def test_operation(uow: AsyncUnitOfWork) -> str:
            return "operation_result"

        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            result = await service._execute_in_transaction(test_operation)

            assert result == "operation_result"
            mock_uow_class.return_value.__aenter__.assert_awaited_once()

    async def test_execute_in_transaction_with_exception_reraise_true(self) -> None:
        """
        GIVEN a TransactionalService instance
        WHEN calling _execute_in_transaction with a failing operation and reraise=True
        THEN it should reraise the exception
        """
        service = TransactionalService()
        test_exception = ValueError("Operation failed")

        async def failing_operation(uow: AsyncUnitOfWork) -> str:
            raise test_exception

        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            with pytest.raises(ValueError, match="Operation failed"):
                await service._execute_in_transaction(failing_operation, reraise=True)

    async def test_execute_in_transaction_with_exception_reraise_false(self) -> None:
        """
        GIVEN a TransactionalService instance
        WHEN calling _execute_in_transaction with a failing operation and reraise=False
        THEN it should return None
        """
        service = TransactionalService()
        test_exception = ValueError("Operation failed")

        async def failing_operation(uow: AsyncUnitOfWork) -> str:
            raise test_exception

        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            result = await service._execute_in_transaction(failing_operation, reraise=False)

            assert result is None

    async def test_transaction_context_manager(self) -> None:
        """
        GIVEN a TransactionalService instance
        WHEN using the transaction context manager
        THEN it should provide access to a UoW instance
        """
        service = TransactionalService()

        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            async with service.transaction() as uow:
                assert uow is mock_uow

            mock_uow_class.return_value.__aenter__.assert_awaited_once()


class TestWithTransaction:
    """Test the with_transaction convenience function."""

    async def test_with_transaction_success(self) -> None:
        """
        GIVEN the with_transaction convenience function
        WHEN executing a successful operation
        THEN it should return the operation result
        """

        async def test_operation(uow: AsyncUnitOfWork) -> str:
            return "operation_result"

        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            result = await with_transaction(test_operation)

            assert result == "operation_result"
            mock_uow_class.return_value.__aenter__.assert_awaited_once()

    async def test_with_transaction_with_exception(self) -> None:
        """
        GIVEN the with_transaction convenience function
        WHEN executing a failing operation
        THEN it should propagate the exception
        """
        test_exception = ValueError("Operation failed")

        async def failing_operation(uow: AsyncUnitOfWork) -> str:
            raise test_exception

        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            with pytest.raises(ValueError, match="Operation failed"):
                await with_transaction(failing_operation)


class TestBulkTransactionManager:
    """Test the BulkTransactionManager class."""

    async def test_bulk_transaction_manager_empty_operations(self) -> None:
        """
        GIVEN a BulkTransactionManager with no operations
        WHEN executing all operations
        THEN it should return an empty list
        """
        manager = BulkTransactionManager()
        results = await manager.execute_all()
        assert results == []

    async def test_bulk_transaction_manager_successful_operations(self) -> None:
        """
        GIVEN a BulkTransactionManager with multiple operations
        WHEN all operations succeed
        THEN it should return results from all operations
        """
        manager = BulkTransactionManager()

        async def operation1(uow: AsyncUnitOfWork) -> str:
            return "result1"

        async def operation2(uow: AsyncUnitOfWork) -> str:
            return "result2"

        manager.add_operation(operation1)
        manager.add_operation(operation2)

        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            results = await manager.execute_all()

            assert results == ["result1", "result2"]
            mock_uow_class.return_value.__aenter__.assert_awaited_once()

    async def test_bulk_transaction_manager_with_failing_operation(self) -> None:
        """
        GIVEN a BulkTransactionManager with multiple operations where one fails
        WHEN executing all operations
        THEN it should raise the exception from the failing operation
        """
        manager = BulkTransactionManager()
        test_exception = ValueError("Operation 2 failed")

        async def operation1(uow: AsyncUnitOfWork) -> str:
            return "result1"

        async def failing_operation(uow: AsyncUnitOfWork) -> str:
            raise test_exception

        manager.add_operation(operation1)
        manager.add_operation(failing_operation)

        with patch("app.shared.transaction.AsyncUnitOfWork") as mock_uow_class:
            mock_uow = AsyncMock()
            mock_uow_class.return_value.__aenter__.return_value = mock_uow

            with pytest.raises(ValueError, match="Operation 2 failed"):
                await manager.execute_all()

    def test_bulk_transaction_manager_clear(self) -> None:
        """
        GIVEN a BulkTransactionManager with operations
        WHEN calling clear()
        THEN it should remove all registered operations
        """
        manager = BulkTransactionManager()

        async def dummy_operation(uow: AsyncUnitOfWork) -> str:
            return "result"

        manager.add_operation(dummy_operation)
        assert len(manager._operations) == 1

        manager.clear()
        assert len(manager._operations) == 0
