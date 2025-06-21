from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.domain.profiles.models import Profile
from app.domain.users.models import UserWithToken
from app.main import app
from app.api.users import get_current_user


@pytest.mark.asyncio
async def test_get_profile_not_found():
    fake_user = UserWithToken(
        username="johndoe",
        email="johndoe@email.com",
        bio="bio",
        image="img",
        token="token",
    )
    async def override_get_current_user():
        return fake_user
    app.dependency_overrides[get_current_user] = override_get_current_user
    with patch(
        "app.service_layer.profiles.services.get_profile_by_username",
        new=AsyncMock(side_effect=Exception("Profile not found")),
    ):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/profiles/nonexistentuser")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_profile_unauthenticated():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/profiles/nonexistentuser")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_profile_success():
    fake_profile = Profile(username="johndoe", bio="bio", image="img", following=False)
    fake_user = UserWithToken(
        username="johndoe",
        email="johndoe@email.com",
        bio="bio",
        image="img",
        token="token",
    )
    async def override_get_current_user():
        return fake_user
    app.dependency_overrides[get_current_user] = override_get_current_user
    with patch(
        "app.api.profiles.get_profile_by_username",
        new=AsyncMock(return_value=fake_profile),
    ):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/profiles/johndoe")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "profile" in data
        assert data["profile"]["username"] == "johndoe"
        assert data["profile"]["bio"] == "bio"
        assert data["profile"]["image"] == "img"
        assert data["profile"]["following"] is False
    app.dependency_overrides.clear()
