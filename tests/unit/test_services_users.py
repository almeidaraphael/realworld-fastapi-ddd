from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.users.exceptions import UserAlreadyExistsError
from app.domain.users.schemas import (
    NewUserRequest,
    UserCreate,
    UserRead,
    UserUpdate,
    UserUpdateRequest,
)
from app.service_layer.users import services


@pytest.fixture
def fake_user() -> MagicMock:
    return MagicMock()


@pytest.fixture
def validated_user() -> UserRead:
    return UserRead(username="u", email="e@e.com", bio="bio", image="img")


@pytest.fixture
def user_update() -> UserUpdateRequest:
    return UserUpdateRequest(user=UserUpdate(bio="bio"))


@pytest.mark.asyncio
async def test_create_user_success(
    mocker: Any,
    patch_repo_users: Any,
    patch_uow_users: tuple[Any, Any],
) -> None:
    """
    GIVEN a valid new user registration request to the service layer
    WHEN create_user_service is called and the user does not already exist
    THEN it should hash the password, add the user, and commit the transaction
    """
    user_data = UserCreate(username="testuser", email="test@example.com", password="p")
    req = NewUserRequest(user=user_data)
    patch_repo_users[1].get_by_username_or_email = AsyncMock(return_value=None)
    patch_repo_users[1].add = AsyncMock(side_effect=lambda user: setattr(user, "id", 1))
    mocker.patch("app.service_layer.users.services.get_password_hash", return_value="hashed")
    _, _ = patch_uow_users

    result = await services.create_user(req)
    assert result.username == user_data.username
    patch_repo_users[1].add.assert_called()
    assert patch_repo_users[1].add.call_args[0][0].hashed_password == "hashed"


@pytest.mark.asyncio
async def test_create_user_duplicate(
    mocker: Any,
    patch_repo_users: Any,
    patch_uow_users: tuple[Any, Any],
) -> None:
    user_data = UserCreate(username="testuser", email="test@example.com", password="p")
    req = NewUserRequest(user=user_data)
    patch_repo_users[1].get_by_username_or_email = AsyncMock(return_value=user_data)
    _, _ = patch_uow_users
    with pytest.raises(UserAlreadyExistsError):
        await services.create_user(req)
