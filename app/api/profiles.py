from fastapi import APIRouter, Depends, HTTPException, status

from app.api.users import get_current_user
from app.domain.profiles.exceptions import (
    CannotFollowYourselfError,
    ProfileNotFoundError,
    UserOrFollowerIdMissingError,
)
from app.domain.profiles.schemas import ProfileRead, ProfileResponse
from app.domain.users.schemas import UserWithToken
from app.service_layer.profiles.services import follow_user, get_profile_by_username, unfollow_user

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
    return ProfileResponse(profile=ProfileRead.model_validate(profile))


@router.post("/{username}/follow", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def follow_profile(
    username: str, current_user: UserWithToken = Depends(get_current_user)
) -> ProfileResponse:
    """
    Follow a user by username.

    Authenticated users can follow another user. Returns the updated profile with following status.
    Returns 400 if attempting to follow yourself, 404 if the profile does not exist, and 500 for
    internal errors.
    """
    try:
        profile = await follow_user(username, current_user.username)
    except CannotFollowYourselfError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UserOrFollowerIdMissingError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ProfileResponse(profile=ProfileRead.model_validate(profile))


@router.delete("/{username}/follow", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def unfollow_profile(
    username: str, current_user: UserWithToken = Depends(get_current_user)
) -> ProfileResponse:
    """
    Unfollow a user by username.

    Authenticated users can unfollow another user.
    Returns the updated profile with the following status:
    Returns 400 if attempting to unfollow yourself, 404 if the profile does not exist,
    and 500 for internal errors.
    """
    try:
        profile = await unfollow_user(username, current_user.username)
    except CannotFollowYourselfError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UserOrFollowerIdMissingError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ProfileResponse(profile=ProfileRead.model_validate(profile))
