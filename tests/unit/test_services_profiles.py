import logging
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.adapters.orm.engine import get_async_engine
from app.domain.profiles.exceptions import (
    CannotFollowYourselfError,
    ProfileNotFoundError,
    UserOrFollowerIdMissingError,
)
from app.service_layer.profiles import services


async def test_get_profile_by_username_not_found(patch_repo_profiles: Any) -> None:
    with pytest.raises(ProfileNotFoundError):
        await services.get_profile_by_username("nonexistent", None)


async def test_follow_user_not_found(patch_repo_profiles: Any) -> None:
    with pytest.raises(ProfileNotFoundError):
        await services.follow_user("nonexistent", "follower")


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


async def test_follow_user_profile_not_found(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    repo.get_by_username_or_email = AsyncMock(side_effect=[None, user_factory.build()])
    mocker.patch.object(services, "UserRepository", return_value=repo)
    with pytest.raises(ProfileNotFoundError):
        await services.follow_user("ghost", "follower")


async def test_follow_user_follower_not_found(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    repo.get_by_username_or_email = AsyncMock(side_effect=[user_factory.build(), None])
    mocker.patch.object(services, "UserRepository", return_value=repo)
    with pytest.raises(ProfileNotFoundError):
        await services.follow_user("target", "ghost")


async def test_follow_user_cannot_follow_self(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    user = user_factory.build(username="same", following=False)
    user.id = 1
    repo.get_by_username_or_email = AsyncMock(side_effect=[user, user])
    mocker.patch.object(services, "UserRepository", return_value=repo)
    with pytest.raises(CannotFollowYourselfError):
        await services.follow_user("same", "same")


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


async def test_unfollow_user_success(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    user = user_factory.build(username="target", following=True)
    user.id = 1
    follower = user_factory.build(username="follower", following=True)
    follower.id = 2
    repo.get_by_username_or_email = AsyncMock(side_effect=[user, follower])
    repo.unfollow_user = AsyncMock()
    mocker.patch.object(services, "UserRepository", return_value=repo)
    result = await services.unfollow_user("target", "follower")
    assert result.username == "target"
    assert result.following is False
    repo.unfollow_user.assert_called_once_with(follower_id=2, followee_id=1)


async def test_unfollow_user_profile_not_found(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    repo.get_by_username_or_email = AsyncMock(side_effect=[None, user_factory.build()])
    mocker.patch.object(services, "UserRepository", return_value=repo)
    with pytest.raises(ProfileNotFoundError):
        await services.unfollow_user("ghost", "follower")


async def test_unfollow_user_follower_not_found(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    repo.get_by_username_or_email = AsyncMock(side_effect=[user_factory.build(), None])
    mocker.patch.object(services, "UserRepository", return_value=repo)
    with pytest.raises(ProfileNotFoundError):
        await services.unfollow_user("target", "ghost")


async def test_unfollow_user_cannot_unfollow_self(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    user = user_factory.build(username="same", following=True)
    user.id = 1
    repo.get_by_username_or_email = AsyncMock(side_effect=[user, user])
    mocker.patch.object(services, "UserRepository", return_value=repo)
    with pytest.raises(CannotFollowYourselfError):
        await services.unfollow_user("same", "same")


async def test_unfollow_user_missing_id(mocker, patch_uow_profiles, user_factory):
    repo = MagicMock()
    user = user_factory.build(username="target", following=True)
    user.id = None
    follower = user_factory.build(username="follower", following=True)
    follower.id = 2
    repo.get_by_username_or_email = AsyncMock(side_effect=[user, follower])
    mocker.patch.object(services, "UserRepository", return_value=repo)
    with pytest.raises(UserOrFollowerIdMissingError):
        await services.unfollow_user("target", "follower")


def test_db_url_is_test_db():
    engine = get_async_engine()
    url = str(engine.url)
    logging.debug(f"[DEBUG] Engine URL: {url}")
    assert "test" in url, f"Engine URL is not a test DB: {url}"
