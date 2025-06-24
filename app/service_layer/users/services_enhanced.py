"""
Enhanced user service with consistent transaction management.

This module demonstrates how to use the new transaction management utilities
for consistent database transaction handling across all service methods.
"""

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
)
from app.events import (
    UserLoggedIn,
    UserLoginAttempted,
    UserPasswordChanged,
    UserProfileUpdated,
    UserRegistered,
    shared_event_bus,
)
from app.shared.transaction import transactional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    hashed: str = pwd_context.hash(password)
    return hashed


@transactional()
async def create_user_enhanced(uow: AsyncUnitOfWork, user_req: NewUserRequest) -> UserRead:
    """
    Create a new user with transaction management.

    This version uses the @transactional decorator to automatically
    handle transaction management. The UoW is injected automatically.
    """
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

    # Transaction is automatically committed by decorator
    return UserRead.model_validate(user.__dict__)


@transactional()
async def authenticate_user_enhanced(
    uow: AsyncUnitOfWork, user_req: UserLoginRequest
) -> UserRead | None:
    """
    Authenticate a user with transaction management.

    This version uses the @transactional decorator for consistent
    transaction handling and error management.
    """
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
async def get_user_by_email_safe(uow: AsyncUnitOfWork, email: str) -> UserRead | None:
    """
    Get user by email with safe error handling.

    This version uses reraise=False to return None on errors instead
    of propagating exceptions. Useful for optional user lookups.
    """
    repo = UserRepository(uow.session)
    user = await repo.get_by_username_or_email("", email)
    if not user:
        return None
    return UserRead.model_validate(user.__dict__)


@transactional()
async def update_user_enhanced(
    uow: AsyncUnitOfWork, email: str, user_update_req: UserUpdateRequest
) -> UserRead:
    """
    Update user with transaction management.

    This version demonstrates complex business logic within a transaction,
    including password hashing and event publishing.
    """
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

    # Transaction is automatically committed by decorator
    return UserRead.model_validate(user.__dict__)


# Example of the original functions for comparison
async def create_user_original(user_req: NewUserRequest) -> UserRead:
    """Original create_user function for comparison."""
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
