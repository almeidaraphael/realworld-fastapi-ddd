from fastapi import APIRouter, Body, Depends, status

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
    favorite_article,
    feed_articles,
    get_article_by_slug,
    list_articles,
    unfavorite_article,
    update_article,
)
from app.service_layer.comments.services import CommentService
from app.shared.exceptions import translate_domain_error_to_http

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
    except (ArticleNotFoundError, ArticlePermissionError) as exc:
        raise translate_domain_error_to_http(exc) from exc
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
        return ArticlesListResponse.model_validate(result)
    except (UserNotFoundError, ArticleNotFoundError) as exc:
        raise translate_domain_error_to_http(exc) from exc


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
        return ArticlesListResponse.model_validate(result)
    except (UserNotFoundError, ArticleNotFoundError) as exc:
        raise translate_domain_error_to_http(exc) from exc


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
        return ArticleResponse.model_validate(result)
    except ArticleNotFoundError as exc:
        raise translate_domain_error_to_http(exc) from exc


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
        return ArticleResponse.model_validate(result)
    except (ArticleNotFoundError, ArticlePermissionError) as exc:
        raise translate_domain_error_to_http(exc) from exc


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
    except (ArticleNotFoundError, ArticlePermissionError) as exc:
        raise translate_domain_error_to_http(exc) from exc


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
        service = CommentService()
        created_comment = await service.add_comment_to_article(
            article_slug=slug,
            comment_data=comment.comment,
            current_user_id=current_user.id,
        )
        return CommentResponse(comment=created_comment)
    except (ArticleNotFoundError, UserNotFoundError) as exc:
        raise translate_domain_error_to_http(exc) from exc


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
        service = CommentService()
        user_id = current_user.id if current_user else None
        comments = await service.get_comments_from_article(
            article_slug=slug,
            current_user_id=user_id,
        )
        return CommentsResponse(comments=comments)
    except ArticleNotFoundError as exc:
        raise translate_domain_error_to_http(exc) from exc


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
        service = CommentService()
        await service.delete_comment(
            article_slug=slug,
            comment_id=comment_id,
            current_user_id=current_user.id,
        )
    except (ArticleNotFoundError, CommentNotFoundError, CommentPermissionError) as exc:
        raise translate_domain_error_to_http(exc) from exc


@router.post(
    "/{slug}/favorite",
    response_model=ArticleResponse,
    status_code=status.HTTP_200_OK,
    summary="Favorite an article",
)
async def favorite_article_endpoint(
    slug: str,
    current_user: UserWithToken = Depends(get_current_user),
) -> ArticleResponse:
    """
    Add an article to user's favorites.
    """
    try:
        result = await favorite_article(slug, current_user)
        return ArticleResponse.model_validate(result)
    except ArticleNotFoundError as exc:
        raise translate_domain_error_to_http(exc) from exc


@router.delete(
    "/{slug}/favorite",
    response_model=ArticleResponse,
    status_code=status.HTTP_200_OK,
    summary="Unfavorite an article",
)
async def unfavorite_article_endpoint(
    slug: str,
    current_user: UserWithToken = Depends(get_current_user),
) -> ArticleResponse:
    """
    Remove an article from user's favorites.
    """
    try:
        result = await unfavorite_article(slug, current_user)
        return ArticleResponse.model_validate(result)
    except ArticleNotFoundError as exc:
        raise translate_domain_error_to_http(exc) from exc
