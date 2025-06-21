from fastapi import APIRouter, Body, HTTPException, status

from app.domain.users.exceptions import UserAlreadyExistsError
from app.domain.users.models import (
    NewUserRequest,
    UserResponse,
    UserWithToken,
)
from app.service_layer.users.services import create_user as create_user_service
from app.shared.jwt import create_access_token

router = APIRouter()

user_body = Body(
    ...,
    examples={
        "default": {
            "summary": "A sample user registration payload",
            "value": {
                "user": {
                    "username": "John Doe",
                    "email": "johndoe@domain.com",
                    "password": "supersecretpwd",
                }
            },
        }
    },  # type: ignore[arg-type]
)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    tags=["User and Authentication"],
)
async def create_user(user: NewUserRequest = user_body) -> UserResponse:
    """
    Register a new user account.

    Creates a new user in the system and returns the user profile with a JWT authentication token.
    On success, returns HTTP 201 and the created user's information.
    Raises 400 if the user already exists.
    """
    try:
        user_data = await create_user_service(user)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    token = create_access_token({"sub": user_data.email})
    user_with_token = UserWithToken(
        email=user_data.email,
        token=token,
        username=user_data.username,
        bio=user_data.bio or "",
        image=user_data.image or "",
    )
    return UserResponse(user=user_with_token)
