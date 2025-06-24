from passlib.context import CryptContext

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.adapters.repository.users import UserRepository
from app.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.domain.users.models import User
from app.domain.users.schemas import (
    NewUserRequest,
    UserLoginRequest,
    UserRead,
    UserUpdateRequest,
    UserWithToken,
)
from app.events import (
    UserLoggedIn,
    UserLoginAttempted,
    UserPasswordChanged,
    UserProfileUpdated,
    UserRegistered,
    shared_event_bus,
)
from app.shared.exceptions import AuthenticationError
from app.shared.jwt import decode_access_token
from app.shared.transaction import transactional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    hashed: str = pwd_context.hash(password)
    return hashed


def _convert_user_to_user_with_token(user: UserRead, token: str) -> UserWithToken:
    """
    Convert a UserRead object to UserWithToken.

    This encapsulates the conversion logic in the service layer.
    """
    return UserWithToken(
        email=user.email,
        token=token,
        username=user.username,
        bio=user.bio or "",
        image=user.image or "",
        id=user.id,
    )


async def _authenticate_user_from_token_impl(uow: AsyncUnitOfWork, token: str) -> UserRead:
    """
    Core implementation for authenticating a user from a JWT token.

    This is a helper function used by both transactional variants.
    """
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise AuthenticationError(
            "Invalid authentication token", error_code="INVALID_TOKEN"
        ) from exc

    email = payload.get("sub")
    if not email or not isinstance(email, str):
        raise AuthenticationError(
            "Invalid authentication credentials", error_code="INVALID_CREDENTIALS"
        )

    repo = UserRepository(uow.session)
    user = await repo.get_by_username_or_email("", email)
    if not user:
        raise AuthenticationError("User not found", error_code="USER_NOT_FOUND")

    return UserRead.model_validate(user.__dict__)


@transactional()
async def authenticate_user_from_token(uow: AsyncUnitOfWork, token: str) -> UserRead:
    """
    Authenticate a user from a JWT token.

    Args:
        uow: Unit of work for database operations
        token: JWT token to validate

    Returns:
        UserRead object for the authenticated user

    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    return await _authenticate_user_from_token_impl(uow, token)


@transactional()
async def authenticate_user_from_token_optional(
    uow: AsyncUnitOfWork, token: str
) -> UserRead | None:
    """
    Authenticate a user from a JWT token, returning None if authentication fails.

    Args:
        uow: Unit of work for database operations
        token: JWT token to validate

    Returns:
        UserRead object for the authenticated user, or None if authentication fails
    """
    try:
        return await _authenticate_user_from_token_impl(uow, token)
    except (AuthenticationError, ValueError):
        return None


@transactional()
async def get_current_user_with_token(uow: AsyncUnitOfWork, token: str) -> UserWithToken:
    """
    Get the current authenticated user as UserWithToken from a JWT token.

    This is the complete authentication workflow that returns a UserWithToken
    object ready for API responses. It handles token validation, user lookup,
    and UserWithToken conversion.

    Args:
        uow: Unit of work for database operations
        token: JWT token to validate

    Returns:
        UserWithToken object for the authenticated user

    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    user = await _authenticate_user_from_token_impl(uow, token)
    return _convert_user_to_user_with_token(user, token)


@transactional()
async def get_current_user_with_token_optional(
    uow: AsyncUnitOfWork, token: str
) -> UserWithToken | None:
    """
    Get the current authenticated user as UserWithToken from a JWT token,
    returning None if authentication fails.

    This is the complete optional authentication workflow that returns a UserWithToken
    object ready for API responses, or None if authentication fails.

    Args:
        uow: Unit of work for database operations
        token: JWT token to validate

    Returns:
        UserWithToken object for the authenticated user, or None if authentication fails
    """
    try:
        user = await _authenticate_user_from_token_impl(uow, token)
        return _convert_user_to_user_with_token(user, token)
    except (AuthenticationError, ValueError):
        return None


@transactional()
async def create_user(uow: AsyncUnitOfWork, user_req: NewUserRequest) -> UserRead:
    """Create a new user with enhanced transaction management."""
    repo = UserRepository(uow.session)
    user_data = user_req.user
    existing = await repo.get_by_username_or_email(user_data.username, user_data.email)
    if existing:
        raise UserAlreadyExistsError("Username or email already registered")
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
    )
    await repo.add(user)
    # Publish user registration event
    if user.id is not None:
        shared_event_bus.publish(
            UserRegistered(user_id=user.id, username=user.username, email=user.email)
        )
    # Transaction automatically committed by decorator
    return UserRead.model_validate(user.__dict__)


@transactional()
async def authenticate_user(uow: AsyncUnitOfWork, user_req: UserLoginRequest) -> UserRead | None:
    """Authenticate a user with enhanced transaction management."""
    repo = UserRepository(uow.session)
    user = await repo.get_by_username_or_email("", user_req.user.email)

    if not user:
        # Publish failed login attempt
        shared_event_bus.publish(UserLoginAttempted(email=user_req.user.email, success=False))
        return None
    if not pwd_context.verify(user_req.user.password, user.hashed_password):
        # Publish failed login attempt
        shared_event_bus.publish(UserLoginAttempted(email=user_req.user.email, success=False))
        return None

    # Publish successful login attempt
    shared_event_bus.publish(UserLoginAttempted(email=user_req.user.email, success=True))

    # Publish user login event
    if user.id is not None:
        shared_event_bus.publish(
            UserLoggedIn(user_id=user.id, username=user.username, email=user.email)
        )
    return UserRead.model_validate(user.__dict__)


@transactional(reraise=False, log_errors=True)
async def get_user_by_email(uow: AsyncUnitOfWork, email: str) -> UserRead | None:
    """
    Get user by email with safe error handling.

    Returns None on error instead of raising exceptions.
    """
    repo = UserRepository(uow.session)
    user = await repo.get_by_username_or_email("", email)
    if not user:
        return None
    return UserRead.model_validate(user.__dict__)


@transactional()
async def update_user(
    uow: AsyncUnitOfWork, email: str, user_update_req: UserUpdateRequest
) -> UserRead:
    """Update user with enhanced transaction management."""
    repo = UserRepository(uow.session)
    user = await repo.get_by_username_or_email("", email)
    if not user:
        raise UserNotFoundError("User not found")
    update_data = user_update_req.user.model_dump(exclude_unset=True)
    updated_fields = list(update_data.keys())
    password_changed = False
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        updated_fields.remove("password")
        updated_fields.append("hashed_password")
        password_changed = True
    for key, value in update_data.items():
        setattr(user, key, value)

    # Publish password change event if password was updated
    if password_changed and user.id is not None:
        shared_event_bus.publish(UserPasswordChanged(user_id=user.id, username=user.username))

    # Publish user profile update event
    if user.id is not None and updated_fields:
        shared_event_bus.publish(
            UserProfileUpdated(
                user_id=user.id, username=user.username, updated_fields=updated_fields
            )
        )
    # Transaction automatically committed by decorator
    return UserRead.model_validate(user.__dict__)


@transactional()
async def get_current_user_with_token_from_request(
    uow: AsyncUnitOfWork, token: str | None
) -> UserWithToken:
    """
    Get the current authenticated user as UserWithToken from a JWT token,
    handling missing token case.

    This function handles the complete authentication workflow including
    checking for missing tokens.

    Args:
        uow: Unit of work for database operations
        token: JWT token to validate, or None if missing

    Returns:
        UserWithToken object for the authenticated user

    Raises:
        AuthenticationError: If token is missing, invalid, or user not found
    """
    if not token:
        raise AuthenticationError(
            "Missing or invalid Authorization header", error_code="MISSING_TOKEN"
        )
    user = await _authenticate_user_from_token_impl(uow, token)
    return _convert_user_to_user_with_token(user, token)


# Keep original functions for backward compatibility during migration
async def create_user_original(user_req: NewUserRequest) -> UserRead:
    """Original create_user function - kept for backward compatibility."""
    async with AsyncUnitOfWork() as uow:
        repo = UserRepository(uow.session)
        user_data = user_req.user
        # Check if user/email already exists
        existing = await repo.get_by_username_or_email(user_data.username, user_data.email)
        if existing:
            raise UserAlreadyExistsError("Username or email already registered")
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )
        await repo.add(user)
        # Publish user registration event
        if user.id is not None:
            shared_event_bus.publish(
                UserRegistered(user_id=user.id, username=user.username, email=user.email)
            )
        # UoW will commit automatically on successful exit
        return UserRead.model_validate(user.__dict__)


async def authenticate_user_original(user_req: UserLoginRequest) -> UserRead | None:
    """Original authenticate_user function - kept for backward compatibility."""
    async with AsyncUnitOfWork() as uow:
        repo = UserRepository(uow.session)
        user = await repo.get_by_username_or_email("", user_req.user.email)

        # Import here to avoid circular imports

        if not user:
            # Publish failed login attempt
            shared_event_bus.publish(UserLoginAttempted(email=user_req.user.email, success=False))
            return None
        if not pwd_context.verify(user_req.user.password, user.hashed_password):
            # Publish failed login attempt
            shared_event_bus.publish(UserLoginAttempted(email=user_req.user.email, success=False))
            return None

        # Publish successful login attempt
        shared_event_bus.publish(UserLoginAttempted(email=user_req.user.email, success=True))

        # Publish user login event
        if user.id is not None:
            shared_event_bus.publish(
                UserLoggedIn(user_id=user.id, username=user.username, email=user.email)
            )
        return UserRead.model_validate(user.__dict__)


async def get_user_by_email_original(email: str) -> UserRead | None:
    """Original get_user_by_email function - kept for backward compatibility."""
    async with AsyncUnitOfWork() as uow:
        repo = UserRepository(uow.session)
        user = await repo.get_by_username_or_email("", email)
        if not user:
            return None
        return UserRead.model_validate(user.__dict__)


async def update_user_original(email: str, user_update_req: UserUpdateRequest) -> UserRead:
    """Original update_user function - kept for backward compatibility."""
    async with AsyncUnitOfWork() as uow:
        repo = UserRepository(uow.session)
        user = await repo.get_by_username_or_email("", email)
        if not user:
            raise UserNotFoundError("User not found")
        update_data = user_update_req.user.model_dump(exclude_unset=True)
        updated_fields = list(update_data.keys())
        password_changed = False
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            updated_fields.remove("password")
            updated_fields.append("hashed_password")
            password_changed = True
        for key, value in update_data.items():
            setattr(user, key, value)

        # Publish password change event if password was updated
        if password_changed and user.id is not None:
            shared_event_bus.publish(UserPasswordChanged(user_id=user.id, username=user.username))

        # Publish user profile update event
        if user.id is not None and updated_fields:
            shared_event_bus.publish(
                UserProfileUpdated(
                    user_id=user.id, username=user.username, updated_fields=updated_fields
                )
            )
        # UoW will commit automatically on successful exit
        return UserRead.model_validate(user.__dict__)
