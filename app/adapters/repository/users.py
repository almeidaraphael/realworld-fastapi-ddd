from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

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
