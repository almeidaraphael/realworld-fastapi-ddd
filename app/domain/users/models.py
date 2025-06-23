from typing import Optional

from sqlmodel import Field, SQLModel

from app.shared import USER_DEFAULT_BIO, USER_DEFAULT_IMAGE


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
