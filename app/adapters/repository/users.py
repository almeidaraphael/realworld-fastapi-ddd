from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.adapters.repository.followers import FollowerRepository
from app.domain.users.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username_or_email(self, username: str, email: str) -> User | None:
        statement = select(User).where((User.username == username) | (User.email == email))
        result = await self.session.exec(statement)
        return result.first()

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def follow_user(self, follower_id: int, followee_id: int) -> None:
        follower_repo = FollowerRepository(self.session)
        await follower_repo.add(follower_id, followee_id)

    async def is_following(self, follower_id: int, followee_id: int) -> bool:
        from app.domain.users.followers import Follower

        exists = await self.session.exec(
            select(Follower.follower_id).where(
                (Follower.follower_id == follower_id) & (Follower.followee_id == followee_id)
            )
        )
        return exists.first() is not None
