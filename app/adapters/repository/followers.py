from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repository.base import AsyncRepository
from app.domain.users.orm import Follower, follower_table


class FollowerRepository(AsyncRepository[Follower]):
    """
    Repository for follower relationship operations.

    Handles following/unfollowing relationships between users.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(self, follower_id: int) -> Follower | None:
        """Get a follower relationship by ID - not typically used."""
        result = await self.session.execute(
            select(Follower).where(follower_table.c.id == follower_id)
        )
        return result.scalars().first()

    async def add_relationship(self, follower_id: int, followee_id: int) -> None:
        """Add a follower relationship if it doesn't exist."""
        exists = await self.session.execute(
            select(Follower).where(
                and_(
                    follower_table.c.follower_id == follower_id,
                    follower_table.c.followee_id == followee_id,
                )
            )
        )
        if exists.scalars().first() is None:
            follower = Follower(follower_id=follower_id, followee_id=followee_id)
            self.session.add(follower)
            await self.session.flush()  # Use flush instead of commit for UoW pattern

    async def remove_relationship(self, follower_id: int, followee_id: int) -> None:
        """Remove a follower relationship if it exists."""
        result = await self.session.execute(
            select(Follower).where(
                and_(
                    follower_table.c.follower_id == follower_id,
                    follower_table.c.followee_id == followee_id,
                )
            )
        )
        instance = result.scalars().first()
        if instance is not None:
            await self.session.delete(instance)
            await self.session.flush()  # Use flush instead of commit for UoW pattern
