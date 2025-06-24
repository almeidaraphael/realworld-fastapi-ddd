# Application services for profiles

import logging

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.adapters.repository.users import UserRepository
from app.domain.profiles.exceptions import (
    CannotFollowYourselfError,
    ProfileNotFoundError,
    UserOrFollowerIdMissingError,
)
from app.domain.profiles.schemas import ProfileRead
from app.events import UserFollowed, UserUnfollowed, shared_event_bus
from app.shared import USER_DEFAULT_BIO, USER_DEFAULT_IMAGE
from app.shared.transaction import transactional

logger = logging.getLogger(__name__)


@transactional()
async def get_profile_by_username(
    uow: AsyncUnitOfWork, username: str, current_user: str | None = None
) -> ProfileRead:
    """Get a user profile with optional following status."""
    user_repo = UserRepository(uow.session)
    user = await user_repo.get_by_username_or_email(username, "")
    if not user:
        raise ProfileNotFoundError("Profile not found")

    following = False
    if current_user and current_user != username:
        follower = await user_repo.get_by_username_or_email(current_user, "")
        if follower and follower.id is not None and user.id is not None:
            following = await user_repo.is_following(follower_id=follower.id, followee_id=user.id)

    return ProfileRead(
        username=user.username,
        bio=user.bio or USER_DEFAULT_BIO,
        image=user.image or USER_DEFAULT_IMAGE,
        following=following,
    )


@transactional()
async def follow_user(uow: AsyncUnitOfWork, username: str, follower_username: str) -> ProfileRead:
    """Follow a user and publish an event."""
    user_repo = UserRepository(uow.session)

    user = await user_repo.get_by_username_or_email(username, "")
    follower = await user_repo.get_by_username_or_email(follower_username, "")

    if not user or not follower:
        raise ProfileNotFoundError("Profile or follower not found")
    if user.username == follower.username:
        raise CannotFollowYourselfError()
    if follower.id is None or user.id is None:
        raise UserOrFollowerIdMissingError("User or follower has no id")

    await user_repo.follow_user(follower_id=follower.id, followee_id=user.id)
    # Publish event
    shared_event_bus.publish(UserFollowed(follower_id=follower.id, followee_id=user.id))

    return ProfileRead(
        username=user.username,
        bio=user.bio or USER_DEFAULT_BIO,
        image=user.image or USER_DEFAULT_IMAGE,
        following=True,
    )


@transactional()
async def unfollow_user(uow: AsyncUnitOfWork, username: str, follower_username: str) -> ProfileRead:
    """Unfollow a user and publish an event."""
    user_repo = UserRepository(uow.session)

    user = await user_repo.get_by_username_or_email(username, "")
    follower = await user_repo.get_by_username_or_email(follower_username, "")

    if not user or not follower:
        raise ProfileNotFoundError("Profile or follower not found")
    if user.username == follower.username:
        raise CannotFollowYourselfError("Cannot unfollow yourself")
    if follower.id is None or user.id is None:
        raise UserOrFollowerIdMissingError("User or follower has no id")

    await user_repo.unfollow_user(follower_id=follower.id, followee_id=user.id)
    # Publish event
    shared_event_bus.publish(UserUnfollowed(follower_id=follower.id, followee_id=user.id))

    return ProfileRead(
        username=user.username,
        bio=user.bio or USER_DEFAULT_BIO,
        image=user.image or USER_DEFAULT_IMAGE,
        following=False,
    )


# Keep original functions for backward compatibility during migration
async def get_profile_by_username_original(
    username: str, current_user: str | None = None
) -> ProfileRead:
    """Original get_profile_by_username function - kept for backward compatibility."""
    async with AsyncUnitOfWork() as uow:
        user_repo = UserRepository(uow.session)
        user = await user_repo.get_by_username_or_email(username, "")
        if not user:
            raise ProfileNotFoundError("Profile not found")

        following = False
        if current_user and current_user != username:
            follower = await user_repo.get_by_username_or_email(current_user, "")
            if follower and follower.id is not None and user.id is not None:
                following = await user_repo.is_following(
                    follower_id=follower.id, followee_id=user.id
                )

        return ProfileRead(
            username=user.username,
            bio=user.bio or USER_DEFAULT_BIO,
            image=user.image or USER_DEFAULT_IMAGE,
            following=following,
        )


async def follow_user_original(username: str, follower_username: str) -> ProfileRead:
    """Original follow_user function - kept for backward compatibility."""
    async with AsyncUnitOfWork() as uow:
        user_repo = UserRepository(uow.session)

        user = await user_repo.get_by_username_or_email(username, "")
        follower = await user_repo.get_by_username_or_email(follower_username, "")

        if not user or not follower:
            raise ProfileNotFoundError("Profile or follower not found")
        if user.username == follower.username:
            raise CannotFollowYourselfError()
        if follower.id is None or user.id is None:
            raise UserOrFollowerIdMissingError("User or follower has no id")

        await user_repo.follow_user(follower_id=follower.id, followee_id=user.id)
        # Publish event
        shared_event_bus.publish(UserFollowed(follower_id=follower.id, followee_id=user.id))

        return ProfileRead(
            username=user.username,
            bio=user.bio or USER_DEFAULT_BIO,
            image=user.image or USER_DEFAULT_IMAGE,
            following=True,
        )


async def unfollow_user_original(username: str, follower_username: str) -> ProfileRead:
    """Original unfollow_user function - kept for backward compatibility."""
    async with AsyncUnitOfWork() as uow:
        user_repo = UserRepository(uow.session)

        user = await user_repo.get_by_username_or_email(username, "")
        follower = await user_repo.get_by_username_or_email(follower_username, "")

        if not user or not follower:
            raise ProfileNotFoundError("Profile or follower not found")
        if user.username == follower.username:
            raise CannotFollowYourselfError("Cannot unfollow yourself")
        if follower.id is None or user.id is None:
            raise UserOrFollowerIdMissingError("User or follower has no id")

        await user_repo.unfollow_user(follower_id=follower.id, followee_id=user.id)
        # Publish event
        shared_event_bus.publish(UserUnfollowed(follower_id=follower.id, followee_id=user.id))

        return ProfileRead(
            username=user.username,
            bio=user.bio or USER_DEFAULT_BIO,
            image=user.image or USER_DEFAULT_IMAGE,
            following=False,
        )
