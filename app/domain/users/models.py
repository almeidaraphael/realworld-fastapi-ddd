"""
Domain model for User and Follower entities.

This module contains pure domain models without any infrastructure dependencies.
These models represent the core business entities for user management and following relationships.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """
    Domain model representing a user in the system.

    This is a pure domain model that contains no infrastructure dependencies.
    It represents the essential attributes and behavior of a user.
    """

    username: str
    email: str
    hashed_password: str
    bio: Optional[str] = ""
    image: Optional[str] = ""
    id: Optional[int] = None


@dataclass
class Follower:
    """
    Domain model representing a follower relationship.

    Represents the many-to-many relationship between users for following.
    """

    follower_id: int
    followee_id: int
