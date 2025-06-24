"""
Repository for comment data access operations.

This module provides the data access layer for comment entities,
handling database operations and queries.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repository.base import AsyncRepository
from app.domain.comments.models import Comment
from app.domain.comments.orm import comment_table


class CommentRepository(AsyncRepository[Comment]):
    """
    Repository for comment data access operations.

    Provides methods for CRUD operations on comments.
    """

    model = Comment
    pk_column = comment_table.c.id

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        super().__init__(session)

    async def list_by_article_id(self, article_id: int) -> list[Comment]:
        """Get all comments for a specific article."""
        statement = (
            select(Comment)
            .where(comment_table.c.article_id == article_id)
            .order_by(comment_table.c.created_at.desc())
        )
        return await self._execute_scalars_query(statement)
