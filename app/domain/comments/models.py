"""
Domain models for Comment entities.

This module contains pure domain models without any infrastructure dependencies.
These models represent the core business entities for comment management.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Comment:
    """
    Domain model representing a comment on an article.

    This is a pure domain model that contains no infrastructure dependencies.
    It represents the essential attributes and behavior of a comment.
    """

    body: str
    article_id: int
    author_id: int
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
