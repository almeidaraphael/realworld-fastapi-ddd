import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.adapters.repository.users import UserRepository


@pytest.mark.asyncio
async def test_add_and_get_by_username_or_email(async_client: AsyncClient, user_factory) -> None:
    """
    GIVEN a new user added to the repository
    WHEN get_by_username_or_email is called with the user's username and email
    THEN it should return the user object with matching username and email
    """
    # Use the app's session via dependency injection if possible, else skip
    # This is a pseudo-integration test, assumes test DB is available
    from app.adapters.orm.engine import get_async_engine

    engine = get_async_engine()
    async with AsyncSession(engine) as session:
        repo = UserRepository(session)
        user = user_factory.build()
        await repo.add(user)
        found = await repo.get_by_username_or_email(user.username, user.email)
        assert found is not None
        assert found.username == user.username
        assert found.email == user.email
