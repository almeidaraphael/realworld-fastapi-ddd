"""
SQLAlchemy ORM models for Comment entities.

This module contains the SQLAlchemy mappings for comment domain models.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import registry

from app.domain.comments.models import Comment
from app.shared.metadata import metadata

mapper_registry = registry()

comment_table = Table(
    "comment",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("body", String, nullable=False),
    Column("article_id", Integer, ForeignKey("article.id", ondelete="CASCADE"), nullable=False),
    Column("author_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", String, nullable=True),
    Column("updated_at", String, nullable=True),
)

# Map the domain model to the SQLAlchemy table
mapper_registry.map_imperatively(Comment, comment_table)
