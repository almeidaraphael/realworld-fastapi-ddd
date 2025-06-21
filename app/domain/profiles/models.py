# Domain models for profiles

from typing import Optional

from sqlmodel import SQLModel


class Profile(SQLModel):
    username: str
    bio: Optional[str] = ""
    image: Optional[str] = ""
    following: bool = False


class ProfileResponse(SQLModel):
    profile: Profile
