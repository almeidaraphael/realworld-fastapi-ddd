import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.domain.profiles.exceptions import CannotFollowYourselfError
from app.domain.profiles.schemas import ProfileRead
from app.domain.users.models import User


@pytest.mark.asyncio
async def test_get_profile_not_found(async_client, override_auth):
    with patch(
        "app.service_layer.profiles.services.get_profile_by_username",
        new=AsyncMock(side_effect=Exception("Profile not found")),
    ):
        response = await async_client.get("/profiles/nonexistentuser")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_profile_unauthenticated(async_client):
    response = await async_client.get("/profiles/nonexistentuser")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_profile_success(async_client, override_auth, fake_user):
    fake_profile = ProfileRead(
        username=fake_user.username,
        bio=fake_user.bio,
        image=fake_user.image,
        following=False,
    )
    with patch(
        "app.api.profiles.get_profile_by_username",
        new=AsyncMock(return_value=fake_profile),
    ):
        response = await async_client.get(f"/profiles/{fake_user.username}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "profile" in data
        assert data["profile"]["username"] == fake_user.username
        assert data["profile"]["bio"] == fake_user.bio
        assert data["profile"]["image"] == fake_user.image
        assert data["profile"]["following"] is False


@pytest.mark.asyncio
async def test_unfollow_profile_success(async_client, override_auth, fake_user, async_session):
    # Ensure the user exists in the DB with a unique email to avoid conflicts
    test_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"{fake_user.username}_{test_id}",
        email=f"{fake_user.username}_{test_id}@email.com",
        bio=fake_user.bio,
        image=fake_user.image,
        hashed_password="notused",
    )
    async_session.add(user)
    await async_session.commit()
    fake_profile = ProfileRead(
        username=fake_user.username,
        bio=fake_user.bio,
        image=fake_user.image,
        following=False,
    )
    with patch(
        "app.api.profiles.unfollow_user",
        new=AsyncMock(return_value=fake_profile),
    ):
        response = await async_client.delete(f"/profiles/{fake_user.username}/follow")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "profile" in data
        assert data["profile"]["username"] == fake_user.username
        assert data["profile"]["following"] is False


@pytest.mark.asyncio
async def test_unfollow_profile_not_found(async_client, override_auth, fake_user):
    with patch(
        "app.service_layer.profiles.services.unfollow_user",
        new=AsyncMock(side_effect=Exception("Profile not found")),
    ):
        response = await async_client.delete("/profiles/nonexistentuser/follow")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_unfollow_profile_cannot_unfollow_self(async_client, override_auth, fake_user):
    with patch(
        "app.api.profiles.unfollow_user",
        new=AsyncMock(side_effect=CannotFollowYourselfError("Cannot unfollow yourself")),
    ):
        response = await async_client.delete(f"/profiles/{fake_user.username}/follow")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot unfollow yourself" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_unfollow_profile_unauthenticated(async_client):
    response = await async_client.delete("/profiles/nonexistentuser/follow")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
