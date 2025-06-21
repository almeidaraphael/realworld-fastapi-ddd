from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.users.exceptions import UserAlreadyExistsError
from app.domain.users.models import (
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


@pytest.fixture
def patch_uow(mocker: Any) -> Any:
    patcher = mocker.patch.object(services, "AsyncUnitOfWork")
    mock_ctx = patcher.return_value.__aenter__.return_value
    # session is always present and non-optional now
    return patcher, mock_ctx


@pytest.fixture
def patch_repo(mocker: Any, fake_user: MagicMock) -> tuple[Any, Any]:
    repo = MagicMock()
    repo.get_by_username_or_email = AsyncMock(return_value=fake_user)
    patcher = mocker.patch.object(services, "UserRepository", return_value=repo)
    return patcher, repo


@pytest.mark.asyncio
async def test_create_user_success(
    mocker: Any,
    patch_repo: Any,
    patch_uow: tuple[Any, Any],
) -> None:
    """
    GIVEN a valid new user registration request to the service layer
    WHEN create_user_service is called and the user does not already exist
    THEN it should hash the password, add the user, and commit the transaction
    """
    user_data = UserCreate(username="testuser", email="test@example.com", password="p")
    req = NewUserRequest(user=user_data)
    patch_repo[1].get_by_username_or_email = AsyncMock(return_value=None)
    patch_repo[1].add = AsyncMock()
    mocker.patch("app.service_layer.users.services.get_password_hash", return_value="hashed")
    _, _ = patch_uow

    result = await services.create_user(req)
    assert result.username == user_data.username
    patch_repo[1].add.assert_called()
    assert patch_repo[1].add.call_args[0][0].hashed_password == "hashed"


@pytest.mark.asyncio
async def test_create_user_duplicate(
    mocker: Any,
    patch_repo: Any,
    patch_uow: tuple[Any, Any],
) -> None:
    user_data = UserCreate(username="testuser", email="test@example.com", password="p")
    req = NewUserRequest(user=user_data)
    patch_repo[1].get_by_username_or_email = AsyncMock(return_value=user_data)
    _, _ = patch_uow
    with pytest.raises(UserAlreadyExistsError):
        await services.create_user(req)
