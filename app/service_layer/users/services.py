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
        await uow.session.commit()
        await uow.session.refresh(user)
        return UserRead.model_validate(user.__dict__)


async def authenticate_user(user_req: UserLoginRequest) -> UserRead | None:
    async with AsyncUnitOfWork() as uow:
        repo = UserRepository(uow.session)
        user = await repo.get_by_username_or_email("", user_req.user.email)
        if not user:
            return None
        if not pwd_context.verify(user_req.user.password, user.hashed_password):
            return None
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
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        for key, value in update_data.items():
            setattr(user, key, value)
        await uow.session.commit()
        await uow.session.refresh(user)
        return UserRead.model_validate(user.__dict__)
