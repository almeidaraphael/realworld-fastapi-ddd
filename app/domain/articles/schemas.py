from typing import Optional

from pydantic import BaseModel, Field


class ArticleCreateRequest(BaseModel):
    title: str
    description: str
    body: str
    tagList: Optional[list[str]] = Field(default_factory=list)


class ArticleResponse(BaseModel):
    article: dict
