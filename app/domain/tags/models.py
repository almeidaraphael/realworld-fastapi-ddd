"""
Domain models for Tag entities.

This module contains pure domain models without any infrastructure dependencies.
These models represent the core business entities for tag management.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Tag:
    """
    Domain model representing a tag in the system.

    This is a pure domain model that contains no infrastructure dependencies.
    It represents the essential attributes of a tag.

    Note: Tags are currently stored as arrays within articles rather than
    as separate entities, but this domain model provides a consistent
    interface for tag operations.
    """

    name: str
    usage_count: int = 0
    id: Optional[int] = None
