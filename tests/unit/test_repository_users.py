import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repository.users import UserRepository
from app.domain.users.models import User
from tests.factories import UserReadFactory


@pytest.mark.asyncio
async def test_add_and_get_by_username_or_email(
    async_session: AsyncSession, user_factory: UserReadFactory
) -> None:
    """
    GIVEN a new user added to the repository
    WHEN get_by_username_or_email is called with the user's username and email
    THEN it should return the user object with matching username and email
    """
    repo = UserRepository(async_session)
    user_data = user_factory.build()
    # Convert to domain User model
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password="test_password",
        bio=user_data.bio,
        image=user_data.image,
    )
    # Use the repository's add method which handles commit
    await repo.add(user)
    found = await repo.get_by_username_or_email(user.username, user.email)
    assert found is not None
    assert found.username == user.username
    assert found.email == user.email
