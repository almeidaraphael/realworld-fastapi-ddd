"""
Pydantic schemas for Tags API endpoints.

This module contains the request and response models for tag-related operations
following the RealWorld API specification.
"""

from pydantic import BaseModel


class TagsResponse(BaseModel):
    """
    Response model for the GET /api/tags endpoint.

    Contains a list of all available tags in the system.
    """

    tags: list[str]

    model_config = {"from_attributes": True}
