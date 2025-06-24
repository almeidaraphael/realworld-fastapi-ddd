import logging

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.orm import Follower, User, follower_table, user_table


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

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
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def follow_user(self, follower_id: int, followee_id: int) -> None:
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

    async def unfollow_user(self, follower_id: int, followee_id: int) -> None:
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

    async def is_following(self, follower_id: int, followee_id: int) -> bool:
        exists = await self.session.execute(
            select(follower_table.c.follower_id).where(
                and_(
                    follower_table.c.follower_id == follower_id,
                    follower_table.c.followee_id == followee_id,
                )
            )
        )
        return exists.scalars().first() is not None
