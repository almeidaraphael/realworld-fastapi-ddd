from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.orm import Follower, follower_table


class FollowerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, follower_id: int, followee_id: int) -> None:
        exists = await self.session.execute(
            select(Follower).where(
                and_(
                    follower_table.c.follower_id == follower_id,
                    follower_table.c.followee_id == followee_id,
                )
            )
        )
        if exists.scalars().first() is None:
            self.session.add(Follower(follower_id=follower_id, followee_id=followee_id))
            await self.session.commit()

    async def remove(self, follower_id: int, followee_id: int) -> None:
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
            await self.session.commit()
