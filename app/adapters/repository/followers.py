from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.users.followers import Follower


class FollowerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, follower_id: int, followee_id: int) -> None:
        exists = await self.session.exec(
            select(Follower).where(
                (Follower.follower_id == follower_id) & (Follower.followee_id == followee_id)
            )
        )
        if exists.first() is None:
            self.session.add(Follower(follower_id=follower_id, followee_id=followee_id))
            await self.session.commit()
