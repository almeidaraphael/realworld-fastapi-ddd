from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api import users as users_api
from app.domain.users.models import User
from app.domain.users.schemas import (
    NewUserRequest,
    UserCreate,
    UserLogin,
    UserLoginRequest,
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
        id=user_obj.id or 1,
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


@pytest.mark.asyncio
async def test_login_user_returns_user_response(user_factory) -> None:
    """
    GIVEN a valid user login request to the API layer
    WHEN the login_user function is called with valid credentials and dependencies are mocked
    THEN it should return a UserResponse with the correct user data and token
    """
    user_obj = user_factory.build()
    user_data = user_obj.model_dump()
    email = user_data["email"]
    user = UserLoginRequest(user=UserLogin(email=email, password="pw"))
    fake_user = build_fake_user(user_obj)
    with patch.object(users_api, "authenticate_user", new=AsyncMock(return_value=fake_user)):
        with patch.object(users_api, "create_access_token", return_value="tok"):
            resp = await users_api.login_user(user)
            assert isinstance(resp, UserResponse)
            assert resp.user.email == email
            assert resp.user.token == "tok"


@pytest.mark.asyncio
async def test_get_current_user_return_statement(user_factory) -> None:
    user_obj = user_factory.build()
    user_data = user_obj.model_dump()
    email = user_data["email"]
    with patch.object(users_api, "decode_access_token", return_value={"sub": email}):
        with patch.object(
            users_api,
            "get_user_by_email",
            new=AsyncMock(
                return_value=UserWithToken(
                    id=1,
                    email=email,
                    token="tok",
                    username=user_obj.username,
                    bio=user_obj.bio,
                    image=user_obj.image,
                )
            ),
        ):
            user = await users_api.get_current_user(token="tok")
            assert isinstance(user, UserWithToken)
            assert user.email == email
            assert user.token == "tok"


@pytest.mark.asyncio
async def test_get_current_user_user_not_found_raises(user_factory) -> None:
    user_obj = user_factory.build()
    user_data = user_obj.model_dump()
    email = user_data["email"]
    with patch.object(users_api, "decode_access_token", return_value={"sub": email}):
        with patch.object(users_api, "get_user_by_email", new=AsyncMock(return_value=None)):
            with pytest.raises(HTTPException) as exc_info:
                await users_api.get_current_user(token="tok")
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "User not found"
