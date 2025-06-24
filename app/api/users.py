from fastapi import APIRouter, Body, Depends, Request, status

from app.domain.users.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.domain.users.schemas import (
    NewUserRequest,
    UserLoginRequest,
    UserResponse,
    UserUpdateRequest,
    UserWithToken,
)
from app.service_layer.users.services import authenticate_user, get_user_by_email
from app.service_layer.users.services import create_user as create_user_service
from app.service_layer.users.services import update_user as update_user_service
from app.shared.exceptions import AuthenticationError, translate_domain_error_to_http
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


def get_token_from_header(request: Request) -> str:
    """
    Extracts the JWT token from the Authorization header using
    the 'Token' scheme only (RealWorld spec).
    Raises 401 if missing or invalid.
    """
    auth: str | None = request.headers.get("Authorization")
    if not auth or not auth.startswith("Token "):
        raise translate_domain_error_to_http(
            AuthenticationError("Missing or invalid Authorization header")
        )
    return auth.removeprefix("Token ").strip()


def get_optional_token_from_header(request: Request) -> str | None:
    """
    Extracts the JWT token from the Authorization header using
    the 'Token' scheme only (RealWorld spec).
    Returns None if missing or invalid instead of raising an exception.
    """
    auth: str | None = request.headers.get("Authorization")
    if not auth or not auth.startswith("Token "):
        return None
    return auth.removeprefix("Token ").strip()


async def get_current_user(token: str = Depends(get_token_from_header)) -> UserWithToken:
    """
    Retrieve the current authenticated user from the JWT token.

    Decodes the JWT token, fetches the user by email, and returns the user profile with token.
    Raises 401 if the token is invalid or the user does not exist.
    """
    payload = decode_access_token(token)
    email = payload.get("sub")
    if not email or not isinstance(email, str):
        raise translate_domain_error_to_http(
            AuthenticationError("Invalid authentication credentials", error_code="")
        )
    try:
        user = await get_user_by_email(email)
    except UserNotFoundError as exc:
        raise translate_domain_error_to_http(exc) from exc
    if not user:
        raise translate_domain_error_to_http(AuthenticationError("User not found", error_code=""))
    return UserWithToken(
        email=user.email,
        token=token,
        username=user.username,
        bio=user.bio or "",
        image=user.image or "",
        id=user.id,
    )


async def get_current_user_optional(
    token: str | None = Depends(get_optional_token_from_header),
) -> UserWithToken | None:
    """
    Retrieve the current authenticated user from the JWT token, or None if not authenticated.

    Decodes the JWT token, fetches the user by email, and returns the user profile with token.
    Returns None if the token is missing, invalid, or the user does not exist.
    """
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email or not isinstance(email, str):
            return None
        user = await get_user_by_email(email)
        if not user:
            return None
        return UserWithToken(
            email=user.email,
            token=token,
            username=user.username,
            bio=user.bio or "",
            image=user.image or "",
            id=user.id,
        )
    except (UserNotFoundError, Exception):
        return None


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
    Raises 409 if the user already exists.
    """
    try:
        user_data = await create_user_service(user)
    except UserAlreadyExistsError as exc:
        raise translate_domain_error_to_http(exc) from exc
    token = create_access_token({"sub": user_data.email})
    user_with_token = UserWithToken(
        email=user_data.email,
        token=token,
        username=user_data.username,
        bio=user_data.bio or "",
        image=user_data.image or "",
        id=user_data.id,
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
    Returns 401 if credentials are invalid.
    """
    user_data = await authenticate_user(user)
    if not user_data:
        raise translate_domain_error_to_http(AuthenticationError("Invalid email or password"))
    token = create_access_token({"sub": user_data.email})
    user_with_token = UserWithToken(
        email=user_data.email,
        token=token,
        username=user_data.username,
        bio=user_data.bio or "",
        image=user_data.image or "",
        id=user_data.id,
    )
    return UserResponse(user=user_with_token)


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
        id=updated_user.id,
    )
    return UserResponse(user=user_with_token)
