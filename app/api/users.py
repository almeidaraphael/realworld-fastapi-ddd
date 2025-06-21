from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.domain.users.models import (
    NewUserRequest,
    UserLoginRequest,
    UserResponse,
    UserUpdateRequest,
    UserWithToken,
)
from app.service_layer.users.services import authenticate_user, get_user_by_email
from app.service_layer.users.services import create_user as create_user_service
from app.service_layer.users.services import update_user as update_user_service
from app.shared.jwt import create_access_token, decode_access_token

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


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


@router.post(
    "/users/login",
    response_model=UserResponse,
    summary="Login for existing user",
    tags=["User and Authentication"],
)
async def login_user(user: UserLoginRequest) -> UserResponse:
    """
    Authenticate an existing user and return a JWT token.

    Accepts email and password, verifies credentials, and returns the user profile with a JWT token.
    Returns 400 if credentials are invalid.
    """
    user_data = await authenticate_user(user)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    token = create_access_token({"sub": user_data.email})
    user_with_token = UserWithToken(
        email=user_data.email,
        token=token,
        username=user_data.username,
        bio=user_data.bio or "",
        image=user_data.image or "",
    )
    return UserResponse(user=user_with_token)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserWithToken:
    """
    Retrieve the current authenticated user from the JWT token.

    Decodes the JWT token, fetches the user by email, and returns the user profile with token.
    Raises 401 if the token is invalid or the user does not exist.
    """
    payload = decode_access_token(token)
    email = payload.get("sub")
    if not email or not isinstance(email, str):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    try:
        user = await get_user_by_email(email)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return UserWithToken(
        email=user.email,
        token=token,
        username=user.username,
        bio=user.bio or "",
        image=user.image or "",
    )


@router.get(
    "/user",
    response_model=UserResponse,
    summary="Get current user",
    tags=["User and Authentication"],
)
async def get_user(current_user: UserWithToken = Depends(get_current_user)) -> UserResponse:
    """
    Get the currently authenticated user's profile.

    Requires a valid JWT token. Returns the user profile with token.
    """
    return UserResponse(user=current_user)


@router.put(
    "/user",
    response_model=UserResponse,
    summary="Update current user",
    tags=["User and Authentication"],
)
async def update_user(
    user_update: UserUpdateRequest,
    current_user: UserWithToken = Depends(get_current_user),
) -> UserResponse:
    """
    Update the current authenticated user's profile.

    Accepts updated user fields and returns the updated user profile with a new JWT token.
    Requires authentication.
    """
    updated_user = await update_user_service(current_user.email, user_update)
    token = create_access_token({"sub": updated_user.email})
    user_with_token = UserWithToken(
        email=updated_user.email,
        token=token,
        username=updated_user.username,
        bio=updated_user.bio or "",
        image=updated_user.image or "",
    )
    return UserResponse(user=user_with_token)
