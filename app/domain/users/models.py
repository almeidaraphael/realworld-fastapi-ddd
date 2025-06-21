from typing import Optional

from sqlmodel import Field, SQLModel

from app.shared import USER_DEFAULT_BIO, USER_DEFAULT_IMAGE

# Domain models for users


class UserBase(SQLModel):
    username: str = Field(index=True)
    email: str = Field(index=True)
    bio: Optional[str] = Field(default=USER_DEFAULT_BIO)
    image: Optional[str] = Field(default=USER_DEFAULT_IMAGE)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    # bio and image inherited


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserRead(UserBase):
    pass


class UserWithToken(UserRead):
    token: str


class UserResponse(SQLModel):
    user: UserWithToken


class NewUserRequest(SQLModel):
    user: UserCreate


class UserLogin(SQLModel):
    email: str
    password: str


class UserLoginRequest(SQLModel):
    user: UserLogin


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    image: Optional[str] = None


class UserUpdateRequest(SQLModel):
    user: UserUpdate
