from fastapi import APIRouter, Depends, HTTPException

from app.api.users import get_current_user
from app.domain.profiles.exceptions import (
    ProfileNotFoundError,
)
from app.domain.profiles.models import ProfileResponse
from app.domain.users.models import UserWithToken
from app.service_layer.profiles.services import get_profile_by_username

router = APIRouter(prefix="/profiles", tags=["Profile"])


@router.get("/{username}", response_model=ProfileResponse)
async def get_profile(
    username: str, current_user: UserWithToken = Depends(get_current_user)
) -> ProfileResponse:
    """
    Retrieve a user's profile by username.

    Returns the profile for the specified username. If the user is authenticated, the response
    includes whether the current user follows the profile.
    Returns 404 if the profile does not exist.
    """
    try:
        profile = await get_profile_by_username(
            username, current_user.username if current_user else None
        )
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProfileResponse(profile=profile)
