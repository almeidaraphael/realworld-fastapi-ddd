"""
Base repository pattern with consistent transaction management.

This module provides abstract base classes for repositories following
DDD principles and proper separation of concerns.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, cast

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    """
    Abstract base repository following DDD principles.

    Transaction management is handled by the Unit of Work pattern,
    not by individual repositories.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    @abstractmethod
    async def add(self, entity: T) -> T:
        """Add an entity to the repository."""
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> T | None:
        """Get an entity by its ID."""
        pass


class AsyncRepository(AbstractRepository[T]):
    """
    Base async repository implementation.

    Provides common CRUD operations without transaction management.
    Transactions are handled by the Unit of Work pattern.
    Subclasses should set `model` and `pk_column` class attributes for generic get_by_id.
    """

    model: type | None = None  # SQLAlchemy model class
    pk_column: Any = None  # SQLAlchemy column for primary key

    async def add(self, entity: T) -> T:
        """Add an entity to the repository without committing."""
        self.session.add(entity)
        await self.session.flush()  # Flush to get ID without committing
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        """Delete an entity from the repository without committing."""
        await self.session.delete(entity)
        await self.session.flush()

    async def get_by_id(self, entity_id: int) -> T | None:
        """
        Get an entity by its ID using the configured model and pk_column.
        Subclasses can override for custom logic.
        """
        if self.model is None or self.pk_column is None:
            raise NotImplementedError(
                "Subclasses must define model and pk_column or override get_by_id."
            )
        from sqlalchemy import select

        statement: Any = select(self.model).where(self.pk_column == entity_id)
        return await self._execute_scalar_query(statement)

    async def _build_paginated_query(
        self, base_query: Any, offset: int = 0, limit: int = 20
    ) -> tuple[list[T], int]:
        """
        Helper method to handle pagination consistently across repositories.

        This eliminates code duplication in list methods.
        """
        # Get paginated results
        paginated_query = base_query.offset(offset).limit(limit)
        result = await self.session.execute(paginated_query)
        entities = list(result.scalars().all())

        # Get total count
        from sqlalchemy import func, select

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        return entities, total

    async def _execute_scalar_query(self, query: Any) -> T | None:
        """
        Execute a query that returns a single scalar result.

        Optimized for async performance with proper exception handling.
        """
        result = await self.session.execute(query)
        return cast(T | None, result.scalars().first())

    async def _execute_scalars_query(self, query: Any) -> list[T]:
        """
        Execute a query that returns multiple scalar results.

        Optimized for async performance with proper result handling.
        """
        result = await self.session.execute(query)
        return list(result.scalars().all())
