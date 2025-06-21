# Application services for profiles

import logging

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.adapters.repository.users import UserRepository
from app.domain.profiles.exceptions import (
    ProfileNotFoundError,
)
from app.domain.profiles.models import Profile
from app.shared import USER_DEFAULT_BIO, USER_DEFAULT_IMAGE

logger = logging.getLogger(__name__)


async def get_profile_by_username(username: str, current_user: str | None = None) -> Profile:
    async with AsyncUnitOfWork() as uow:
        logger.info(f"[DEBUG] get_profile_by_username: Using session {uow.session}")
        repo = UserRepository(uow.session)
        user = await repo.get_by_username_or_email(username, "")
        if not user:
            raise ProfileNotFoundError("Profile not found")
        following = False  # TODO: implement following logic
        return Profile(
            username=user.username,
            bio=user.bio or USER_DEFAULT_BIO,
            image=user.image or USER_DEFAULT_IMAGE,
            following=following,
        )
