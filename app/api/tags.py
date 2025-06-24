"""Tags API endpoints."""

from fastapi import APIRouter, HTTPException

from app.domain.tags.schemas import TagsResponse
from app.service_layer.tags.services import get_tags

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=TagsResponse, summary="Get tags")
async def get_tags_endpoint() -> TagsResponse:
    """
    Get all tags available in the system.

    Returns a list of all unique tags from all articles.
    No authentication required.
    """
    try:
        tags = await get_tags()
        return TagsResponse(tags=tags)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
