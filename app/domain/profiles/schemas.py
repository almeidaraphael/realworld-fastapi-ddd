from typing import Optional

from pydantic import BaseModel


class ProfileRead(BaseModel):
    username: str
    bio: Optional[str] = ""
    image: Optional[str] = ""
    following: bool = False


class ProfileResponse(BaseModel):
    profile: ProfileRead
