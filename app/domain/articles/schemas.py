from typing import Optional

from pydantic import BaseModel, Field


class ArticleCreate(BaseModel):
    title: str
    description: str
    body: str
    tagList: Optional[list[str]] = Field(default_factory=list)


class ArticleCreateRequest(BaseModel):
    article: ArticleCreate


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None


class ArticleUpdateRequest(BaseModel):
    article: ArticleUpdate


class ArticleAuthorOut(BaseModel):
    username: str
    bio: str
    image: str
    following: bool


class ArticleOut(BaseModel):
    slug: str
    title: str
    description: str
    body: str
    tagList: list[str]
    createdAt: str
    updatedAt: str
    favorited: bool
    favoritesCount: int
    author: ArticleAuthorOut


class ArticleResponse(BaseModel):
    article: dict


class ArticlesListResponse(BaseModel):
    articles: list[dict]
    articlesCount: int
