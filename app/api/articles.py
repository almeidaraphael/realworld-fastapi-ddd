from fastapi import APIRouter, Depends, HTTPException, status

from app.api.users import get_current_user
from app.domain.articles.schemas import ArticleCreateRequest, ArticleResponse
from app.domain.users.schemas import UserWithToken
from app.service_layer.articles.services import create_article

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post(
    "",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an article",
)
async def create_article_endpoint(
    article: ArticleCreateRequest,
    current_user: UserWithToken = Depends(get_current_user),
) -> ArticleResponse:
    """
    Create a new article.
    """
    try:
        created = await create_article(article, current_user)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ArticleResponse.model_validate(created)
