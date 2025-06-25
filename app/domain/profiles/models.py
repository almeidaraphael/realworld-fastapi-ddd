"""
Domain models for Profile entities.

This module contains pure domain models without any infrastructure dependencies.
These models represent the core business entities for profile management.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Profile:
    """
    Domain model representing a user profile.

    This is a pure domain model that contains no infrastructure dependencies.
    It represents the essential attributes of a user profile as viewed by others.
    """

    username: str
    bio: Optional[str] = ""
    image: Optional[str] = ""
    following: bool = False
