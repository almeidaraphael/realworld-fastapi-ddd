from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.api.users import get_current_user, get_current_user_optional
from app.domain.articles.exceptions import ArticleNotFoundError, ArticlePermissionError
from app.domain.articles.schemas import (
    ArticleCreateRequest,
    ArticleResponse,
    ArticlesListResponse,
    ArticleUpdateRequest,
)
from app.domain.comments.exceptions import CommentNotFoundError, CommentPermissionError
from app.domain.comments.schemas import (
    CommentCreateRequest,
    CommentResponse,
    CommentsResponse,
)
from app.domain.users.exceptions import UserNotFoundError
from app.domain.users.schemas import UserWithToken
from app.service_layer.articles.services import (
    create_article,
    delete_article,
    feed_articles,
    get_article_by_slug,
    list_articles,
    update_article,
)
from app.service_layer.comments.services import CommentService

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
    try:
        await delete_article(slug, current_user)
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ArticlePermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/{slug}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a comment on an article",
)
async def create_comment_endpoint(
    slug: str,
    comment: CommentCreateRequest = Body(...),
    current_user: UserWithToken = Depends(get_current_user),
) -> CommentResponse:
    """
    Create a new comment on an article.
    """
    try:
        async with AsyncUnitOfWork() as uow:
            service = CommentService(uow)
            created_comment = await service.add_comment_to_article(
                article_slug=slug,
                comment_data=comment.comment,
                current_user_id=current_user.id,
            )
            return CommentResponse(comment=created_comment)
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/{slug}/comments",
    response_model=CommentsResponse,
    summary="Get comments for an article",
)
async def get_comments_endpoint(
    slug: str,
    current_user: UserWithToken | None = Depends(get_current_user_optional),
) -> CommentsResponse:
    """
    Get all comments for an article.
    """
    try:
        async with AsyncUnitOfWork() as uow:
            service = CommentService(uow)
            user_id = current_user.id if current_user else None
            comments = await service.get_comments_from_article(
                article_slug=slug,
                current_user_id=user_id,
            )
            return CommentsResponse(comments=comments)
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete(
    "/{slug}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment from an article",
)
async def delete_comment_endpoint(
    slug: str,
    comment_id: int,
    current_user: UserWithToken = Depends(get_current_user),
) -> None:
    """
    Delete a comment from an article.
    Only the author of the comment can delete it.
    """
    try:
        async with AsyncUnitOfWork() as uow:
            service = CommentService(uow)
            await service.delete_comment(
                article_slug=slug,
                comment_id=comment_id,
                current_user_id=current_user.id,
            )
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CommentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CommentPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
