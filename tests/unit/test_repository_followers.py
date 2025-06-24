import uuid

import pytest
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repository.followers import FollowerRepository
from app.domain.users.models import Follower, User
from app.domain.users.orm import follower_table


@pytest.mark.asyncio
async def test_add_follower_creates_relationship(async_session: AsyncSession) -> None:
    """
    GIVEN two users in the database
    WHEN a follower relationship is added
    THEN the relationship should be created in the database
    """
    # Create users using ORM with unique emails
    test_id = str(uuid.uuid4())[:8]
    follower = User(
        username=f"follower_{test_id}",
        email=f"follower_{test_id}@example.com",
        hashed_password="x",
    )
    followee = User(
        username=f"followee_{test_id}",
        email=f"followee_{test_id}@example.com",
        hashed_password="x",
    )
    async_session.add(follower)
    async_session.add(followee)
    await async_session.commit()

    # Refresh objects to ensure attributes are loaded
    await async_session.refresh(follower)
    await async_session.refresh(followee)

    # Get the auto-assigned IDs
    assert follower.id is not None
    assert followee.id is not None
    follower_id = follower.id
    followee_id = followee.id

    repo = FollowerRepository(async_session)
    await repo.add_relationship(follower_id, followee_id)
    result = await async_session.execute(
        select(Follower).where(
            and_(
                follower_table.c.follower_id == follower_id,
                follower_table.c.followee_id == followee_id,
            )
        )
    )
    assert result.scalars().first() is not None


@pytest.mark.asyncio
async def test_add_follower_idempotent(async_session: AsyncSession) -> None:
    """
    GIVEN two users in the database
    WHEN a follower relationship is added twice
    THEN only one relationship should exist
    """
    # Create users using ORM with unique emails
    test_id = str(uuid.uuid4())[:8]
    follower = User(
        username=f"follower2_{test_id}",
        email=f"follower2_{test_id}@example.com",
        hashed_password="x",
    )
    followee = User(
        username=f"followee2_{test_id}",
        email=f"followee2_{test_id}@example.com",
        hashed_password="x",
    )
    async_session.add(follower)
    async_session.add(followee)
    await async_session.commit()

    # Refresh objects to ensure attributes are loaded
    await async_session.refresh(follower)
    await async_session.refresh(followee)

    # Get the auto-assigned IDs
    assert follower.id is not None
    assert followee.id is not None
    follower_id = follower.id
    followee_id = followee.id

    repo = FollowerRepository(async_session)
    await repo.add_relationship(follower_id, followee_id)
    await repo.add_relationship(follower_id, followee_id)  # Should not raise or duplicate
    result = await async_session.execute(
        select(Follower).where(
            and_(
                follower_table.c.follower_id == follower_id,
                follower_table.c.followee_id == followee_id,
            )
        )
    )
    assert len(result.scalars().all()) == 1


@pytest.mark.asyncio
async def test_remove_follower_removes_relationship(async_session: AsyncSession) -> None:
    """
    GIVEN two users with a follower relationship
    WHEN the relationship is removed
    THEN the relationship should no longer exist in the database
    """
    # Create users using ORM with unique emails
    test_id = str(uuid.uuid4())[:8]
    follower = User(
        username=f"follower_rm_{test_id}",
        email=f"follower_rm_{test_id}@example.com",
        hashed_password="x",
    )
    followee = User(
        username=f"followee_rm_{test_id}",
        email=f"followee_rm_{test_id}@example.com",
        hashed_password="x",
    )
    async_session.add(follower)
    async_session.add(followee)
    await async_session.commit()

    # Refresh objects to ensure attributes are loaded
    await async_session.refresh(follower)
    await async_session.refresh(followee)

    # Get the auto-assigned IDs
    assert follower.id is not None
    assert followee.id is not None
    follower_id = follower.id
    followee_id = followee.id

    repo = FollowerRepository(async_session)
    await repo.add_relationship(follower_id, followee_id)
    # Now remove
    await repo.remove_relationship(follower_id, followee_id)
    result = await async_session.execute(
        select(Follower).where(
            and_(
                follower_table.c.follower_id == follower_id,
                follower_table.c.followee_id == followee_id,
            )
        )
    )
    assert result.scalars().first() is None
