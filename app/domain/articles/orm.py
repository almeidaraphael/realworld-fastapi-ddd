"""
SQLAlchemy ORM mapping for Article and ArticleFavorite domain models.
"""

import datetime

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import registry

from app.domain.articles.models import Article, ArticleFavorite
from app.shared.metadata import metadata

mapper_registry = registry()


def utcnow_naive() -> datetime.datetime:
    """Return current UTC time as a naive datetime (no tzinfo)."""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


article_table = Table(
    "article",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("slug", String, unique=True, nullable=False),
    Column("title", String, nullable=False),
    Column("description", String, nullable=False),
    Column("body", Text, nullable=False),
    Column("tagList", ARRAY(String), default=list),
    Column("author_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("created_at", DateTime, default=utcnow_naive),
    Column("updated_at", DateTime, default=utcnow_naive, onupdate=utcnow_naive),
)

article_favorite_table = Table(
    "article_favorite",
    metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("article_id", Integer, ForeignKey("article.id"), primary_key=True),
)

mapper_registry.map_imperatively(Article, article_table)
mapper_registry.map_imperatively(ArticleFavorite, article_favorite_table)
