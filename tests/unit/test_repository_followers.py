import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.adapters.repository.followers import FollowerRepository
from app.domain.users.followers import Follower
from app.domain.users.models import User


@pytest.mark.asyncio
async def test_add_follower_creates_relationship(async_session: AsyncSession) -> None:
    # Create users using ORM
    follower = User(id=1, username="follower", email="follower@example.com", hashed_password="x")
    followee = User(id=2, username="followee", email="followee@example.com", hashed_password="x")
    async_session.add(follower)
    async_session.add(followee)
    await async_session.commit()
    repo = FollowerRepository(async_session)
    await repo.add(1, 2)
    result = await async_session.exec(
        select(Follower).where(Follower.follower_id == 1, Follower.followee_id == 2)
    )
    assert result.first() is not None


@pytest.mark.asyncio
async def test_add_follower_idempotent(async_session: AsyncSession) -> None:
    # Create users using ORM
    follower = User(id=3, username="follower2", email="follower2@example.com", hashed_password="x")
    followee = User(id=4, username="followee2", email="followee2@example.com", hashed_password="x")
    async_session.add(follower)
    async_session.add(followee)
    await async_session.commit()
    repo = FollowerRepository(async_session)
    await repo.add(3, 4)
    await repo.add(3, 4)  # Should not raise or duplicate
    result = await async_session.exec(
        select(Follower).where(Follower.follower_id == 3, Follower.followee_id == 4)
    )
    assert len(result.all()) == 1
