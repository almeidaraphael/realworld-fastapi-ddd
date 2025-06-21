from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.profiles.exceptions import (
    CannotFollowYourselfError,
    ProfileNotFoundError,
    UserOrFollowerIdMissingError,
)
from app.service_layer.profiles import services


@pytest.mark.asyncio
async def test_get_profile_by_username_not_found(patch_repo_profiles: Any) -> None:
    with pytest.raises(ProfileNotFoundError):
        await services.get_profile_by_username("nonexistent", None)


@pytest.mark.asyncio
async def test_follow_user_not_found(patch_repo_profiles: Any) -> None:
    with pytest.raises(ProfileNotFoundError):
        await services.follow_user("nonexistent", "follower")


@pytest.mark.asyncio
async def test_get_profile_by_username_following_true(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    user = user_factory.build(username="target", following=False)
    user.id = 1
    follower = user_factory.build(username="follower", following=False)
    follower.id = 2
    repo.get_by_username_or_email = AsyncMock(side_effect=[user, follower])
    repo.is_following = AsyncMock(return_value=True)
    mocker.patch.object(services, "UserRepository", return_value=repo)
    result = await services.get_profile_by_username("target", "follower")
    assert result.following is True
    repo.is_following.assert_called_once_with(follower_id=2, followee_id=1)


@pytest.mark.asyncio
async def test_get_profile_by_username_same_user(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    user = user_factory.build(username="same", following=False)
    user.id = 1
    repo.get_by_username_or_email = AsyncMock(return_value=user)
    repo.is_following = AsyncMock()
    mocker.patch.object(services, "UserRepository", return_value=repo)
    result = await services.get_profile_by_username("same", "same")
    assert result.following is False
    repo.is_following.assert_not_called()


@pytest.mark.asyncio
async def test_get_profile_by_username_follower_not_found(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    user = user_factory.build(username="target", following=False)
    user.id = 1
    repo.get_by_username_or_email = AsyncMock(side_effect=[user, None])
    repo.is_following = AsyncMock()
    mocker.patch.object(services, "UserRepository", return_value=repo)
    result = await services.get_profile_by_username("target", "ghost")
    assert result.following is False
    repo.is_following.assert_not_called()


@pytest.mark.asyncio
async def test_follow_user_profile_not_found(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    repo.get_by_username_or_email = AsyncMock(side_effect=[None, user_factory.build()])
    mocker.patch.object(services, "UserRepository", return_value=repo)
    with pytest.raises(ProfileNotFoundError):
        await services.follow_user("ghost", "follower")


@pytest.mark.asyncio
async def test_follow_user_follower_not_found(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    repo.get_by_username_or_email = AsyncMock(side_effect=[user_factory.build(), None])
    mocker.patch.object(services, "UserRepository", return_value=repo)
    with pytest.raises(ProfileNotFoundError):
        await services.follow_user("target", "ghost")


@pytest.mark.asyncio
async def test_follow_user_cannot_follow_self(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    user = user_factory.build(username="same", following=False)
    user.id = 1
    repo.get_by_username_or_email = AsyncMock(side_effect=[user, user])
    mocker.patch.object(services, "UserRepository", return_value=repo)
    with pytest.raises(CannotFollowYourselfError):
        await services.follow_user("same", "same")


@pytest.mark.asyncio
async def test_follow_user_missing_id(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    user = user_factory.build(username="target", following=False)
    user.id = None
    follower = user_factory.build(username="follower", following=False)
    follower.id = 2
    repo.get_by_username_or_email = AsyncMock(side_effect=[user, follower])
    mocker.patch.object(services, "UserRepository", return_value=repo)
    with pytest.raises(UserOrFollowerIdMissingError):
        await services.follow_user("target", "follower")
