"""
Repository for comment data access operations.

This module provides the data access layer for comment entities,
handling database operations and queries.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.comments.models import Comment
from app.domain.comments.orm import comment_table


class CommentRepository:
    """
    Repository for comment data access operations.

    Provides methods for CRUD operations on comments.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def add(self, comment: Comment) -> Comment:
        """Add a new comment to the database."""
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def get_by_id(self, comment_id: int) -> Comment | None:
        """Get a comment by its ID."""
        result = await self.session.execute(select(Comment).where(comment_table.c.id == comment_id))
        return result.scalars().first()

    async def list_by_article_id(self, article_id: int) -> list[Comment]:
        """Get all comments for a specific article."""
        result = await self.session.execute(
            select(Comment)
            .where(comment_table.c.article_id == article_id)
            .order_by(comment_table.c.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, comment: Comment) -> None:
        """Delete a comment from the database."""
        await self.session.delete(comment)
        await self.session.commit()
