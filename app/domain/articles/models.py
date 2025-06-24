"""
Domain model for Article and ArticleFavorite entities.

This module contains pure domain models without any infrastructure dependencies.
These models represent the core business entities for article management.
"""

import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Article:
    """
    Domain model representing an article in the system.

    Contains all the essential attributes of an article including metadata
    for creation and modification tracking.
    """

    title: str
    description: str
    body: str
    author_id: int
    slug: str = ""
    tagList: Optional[list[str]] = None
    id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    def __post_init__(self) -> None:
        """Initialize default values after object creation."""
        if self.tagList is None:
            self.tagList = []


@dataclass
class ArticleFavorite:
    """
    Domain model representing a user's favorite article relationship.

    This represents the many-to-many relationship between users and their
    favorited articles.
    """

    user_id: int
    article_id: int
