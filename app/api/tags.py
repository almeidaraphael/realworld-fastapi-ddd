"""Tags API endpoints."""

from fastapi import APIRouter

from app.domain.tags.schemas import TagsResponse
from app.service_layer.tags.services import get_tags
from app.shared.exceptions import DomainError, translate_domain_error_to_http

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
        raise translate_domain_error_to_http(DomainError(str(exc))) from exc
