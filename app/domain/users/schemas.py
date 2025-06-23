from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    bio: Optional[str] = None
    image: Optional[str] = None


class UserWithToken(UserRead):
    token: str
    id: int


class UserResponse(BaseModel):
    user: UserWithToken


class NewUserRequest(BaseModel):
    user: UserCreate


class UserLogin(BaseModel):
    email: str
    password: str


class UserLoginRequest(BaseModel):
    user: UserLogin


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    image: Optional[str] = None


class UserUpdateRequest(BaseModel):
    user: UserUpdate
