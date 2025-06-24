from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.api.users import get_current_user, get_current_user_optional
from app.domain.articles.schemas import (
    ArticleCreateRequest,
    ArticleResponse,
    ArticlesListResponse,
    ArticleUpdateRequest,
)
from app.domain.users.schemas import UserWithToken
from app.service_layer.articles.services import (
    create_article,
    delete_article,
    feed_articles,
    get_article_by_slug,
    list_articles,
    update_article,
)

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post(
    "",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an article",
)
async def create_article_endpoint(
    article: ArticleCreateRequest = Body(...),
    current_user: UserWithToken = Depends(get_current_user),
) -> ArticleResponse:
    """
    Create a new article.
    """
    try:
        created = await create_article(article.article, current_user)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ArticleResponse.model_validate(created)


@router.get(
    "",
    response_model=ArticlesListResponse,
    summary="List articles",
)
async def get_articles(
    tag: str | None = None,
    author: str | None = None,
    favorited: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> ArticlesListResponse:
    """
    List articles with optional filters and pagination.
    """
    try:
        result = await list_articles(
            tag=tag, author=author, favorited_by=favorited, limit=limit, offset=offset
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ArticlesListResponse.model_validate(result)


@router.get(
    "/feed",
    response_model=ArticlesListResponse,
    summary="Get articles feed",
)
async def get_feed(
    limit: int = 20,
    offset: int = 0,
    current_user: UserWithToken = Depends(get_current_user),
) -> ArticlesListResponse:
    """
    Get articles from users that the current user follows.
    """
    try:
        result = await feed_articles(current_user, limit=limit, offset=offset)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ArticlesListResponse.model_validate(result)


@router.get(
    "/{slug}",
    response_model=ArticleResponse,
    summary="Get an article by slug",
)
async def get_article(
    slug: str,
    current_user: UserWithToken | None = Depends(get_current_user_optional),
) -> ArticleResponse:
    """
    Get a single article by its slug.
    """
    from app.domain.articles.exceptions import ArticleNotFoundError

    try:
        result = await get_article_by_slug(slug, current_user)
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ArticleResponse.model_validate(result)


@router.put(
    "/{slug}",
    response_model=ArticleResponse,
    summary="Update an article",
)
async def update_article_endpoint(
    slug: str,
    article: ArticleUpdateRequest = Body(...),
    current_user: UserWithToken = Depends(get_current_user),
) -> ArticleResponse:
    """
    Update an existing article by slug.

    Only the author of the article can update it.
    """
    from app.domain.articles.exceptions import ArticleNotFoundError, ArticlePermissionError

    try:
        result = await update_article(slug, article.article, current_user)
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ArticlePermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ArticleResponse.model_validate(result)


@router.delete(
    "/{slug}",
    status_code=status.HTTP_200_OK,
    summary="Delete an article",
)
async def delete_article_endpoint(
    slug: str,
    current_user: UserWithToken = Depends(get_current_user),
) -> None:
    """
    Delete an existing article by slug.

    Only the author of the article can delete it.
    """
    from app.domain.articles.exceptions import ArticleNotFoundError, ArticlePermissionError

    try:
        await delete_article(slug, current_user)
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ArticlePermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
