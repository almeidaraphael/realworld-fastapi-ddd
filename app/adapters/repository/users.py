import logging

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repository.base import AsyncRepository
from app.domain.users.orm import User, follower_table, user_table


class UserRepository(AsyncRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_username_or_email(self, username: str, email: str) -> User | None:
        statement = select(User).where(
            or_(user_table.c.username == username, user_table.c.email == email)
        )
        result = await self.session.execute(statement)
        user = result.scalars().first()
        logging.debug(
            "[get_by_username_or_email] username=%s, email=%s, found=%s", username, email, user
        )
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """Get a user by their ID."""
        statement = select(User).where(user_table.c.id == user_id)
        return await self._execute_scalar_query(statement)

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def is_following(self, follower_id: int, followee_id: int) -> bool:
        """Check if a user is following another user."""
        exists = await self.session.execute(
            select(follower_table.c.follower_id).where(
                and_(
                    follower_table.c.follower_id == follower_id,
                    follower_table.c.followee_id == followee_id,
                )
            )
        )
        return exists.scalars().first() is not None

    # Backward compatibility methods - delegate to FollowerRepository
    async def follow_user(self, follower_id: int, followee_id: int) -> None:
        """Follow a user - delegates to FollowerRepository for consistency."""
        from app.adapters.repository.followers import FollowerRepository

        follower_repo = FollowerRepository(self.session)
        await follower_repo.add_relationship(follower_id, followee_id)

    async def unfollow_user(self, follower_id: int, followee_id: int) -> None:
        """Unfollow a user - delegates to FollowerRepository for consistency."""
        from app.adapters.repository.followers import FollowerRepository

        follower_repo = FollowerRepository(self.session)
        await follower_repo.remove_relationship(follower_id, followee_id)
