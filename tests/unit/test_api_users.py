from unittest.mock import AsyncMock, patch

import pytest

from app.api import users as users_api
from app.domain.users.models import (
    NewUserRequest,
    User,
    UserCreate,
    UserResponse,
    UserWithToken,
)


def build_fake_user(user_obj: User, token: str = "tok") -> UserWithToken:
    return UserWithToken(
        email=user_obj.email,
        token=token,
        username=user_obj.username,
        bio=user_obj.bio,
        image=user_obj.image,
    )


@pytest.mark.asyncio
async def test_create_user_returns_user_response(user_factory) -> None:
    """
    GIVEN a valid new user registration request to the API layer
    WHEN the create_user function is called with valid data and dependencies are mocked
    THEN it should return a UserResponse with the correct user data and token
    """
    user_obj = user_factory.build()
    user_data = user_obj.model_dump()
    username = user_data["username"]
    email = user_data["email"]
    user = NewUserRequest(user=UserCreate(username=username, email=email, password="pw"))
    fake_user = build_fake_user(user_obj)
    with patch.object(users_api, "create_user_service", new=AsyncMock(return_value=fake_user)):
        with patch.object(users_api, "create_access_token", return_value="tok"):
            resp = await users_api.create_user(user)
            assert isinstance(resp, UserResponse)
            assert resp.user.email == email
            assert resp.user.token == "tok"
