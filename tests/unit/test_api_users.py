from unittest.mock import AsyncMock, Mock, patch

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


async def test_get_current_user_return_statement(user_factory) -> None:
    """
    GIVEN a valid user and token
    WHEN get_current_user is called
    THEN it should return the user with token
    """
    user_obj = user_factory.build()
    email = user_obj.email

    mock_request = Mock()
    mock_request.headers = {"Authorization": "Token valid_token"}

    with patch.object(
        users_api,
        "get_current_user_with_token_from_request",
        new=AsyncMock(
            return_value=UserWithToken(
                email=email,
                token="valid_token",
                username=user_obj.username,
                bio=user_obj.bio or "",
                image=user_obj.image or "",
                id=user_obj.id,
            )
        ),
    ):
        user = await users_api.get_current_user(mock_request)
        assert isinstance(user, UserWithToken)
        assert user.email == email
        assert user.token == "valid_token"


async def test_get_current_user_user_not_found_raises(user_factory) -> None:
    """
    GIVEN an invalid token that results in user not found
    WHEN get_current_user is called
    THEN it should raise HTTPException with 401 status
    """
    mock_request = Mock()
    mock_request.headers = {"Authorization": "Token invalid_token"}

    from app.shared.exceptions import AuthenticationError

    with patch.object(
        users_api,
        "get_current_user_with_token_from_request",
        new=AsyncMock(side_effect=AuthenticationError("User not found")),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await users_api.get_current_user(mock_request)
        assert exc_info.value.status_code == 401
        assert "AuthenticationError: User not found" in exc_info.value.detail
