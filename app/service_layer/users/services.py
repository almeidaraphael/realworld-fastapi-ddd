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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    hashed: str = pwd_context.hash(password)
    return hashed


async def create_user(user_req: NewUserRequest) -> UserRead:
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


async def authenticate_user(user_req: UserLoginRequest) -> UserRead | None:
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


async def get_user_by_email(email: str) -> UserRead | None:
    async with AsyncUnitOfWork() as uow:
        repo = UserRepository(uow.session)
        user = await repo.get_by_username_or_email("", email)
        if not user:
            return None
        return UserRead.model_validate(user.__dict__)


async def update_user(email: str, user_update_req: UserUpdateRequest) -> UserRead:
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
