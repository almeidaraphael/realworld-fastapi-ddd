from typing import Optional

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str
    title: str
    description: str
    body: str
    tagList: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    author_id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
