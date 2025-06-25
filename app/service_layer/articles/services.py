import secrets
from datetime import datetime, timezone

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.adapters.repository.articles import ArticleRepository
from app.adapters.repository.users import UserRepository
from app.domain.articles.exceptions import ArticleNotFoundError, ArticlePermissionError
from app.domain.articles.orm import Article, article_favorite_table
from app.domain.articles.schemas import ArticleAuthorOut, ArticleCreate, ArticleOut, ArticleUpdate
from app.domain.users.orm import User
from app.domain.users.schemas import UserWithToken
from app.events import (
    ArticleCreated,
    ArticleDeleted,
    ArticleFavorited,
    ArticleUnfavorited,
    ArticleUpdated,
    shared_event_bus,
)
from app.shared.transaction import transactional


def _build_article_response(
    article: Article,
    author_obj: User | None,
    following: bool,
    favorited: bool = False,
    favorites_count: int = 0,
) -> ArticleOut:
    """Builds the ArticleOut schema from SQLAlchemy models."""
    author_data = ArticleAuthorOut(
        username=getattr(author_obj, "username", "") if author_obj else "",
        bio=getattr(author_obj, "bio", "") if author_obj else "",
        image=getattr(author_obj, "image", "") if author_obj else "",
        following=following,
    )
    favorited_bool = bool(favorited)

    # Handle datetime to string conversion safely
    created_at_str = ""
    if article.created_at is not None:
        if hasattr(article.created_at, "isoformat"):
            created_at_str = article.created_at.isoformat()
        else:
            created_at_str = str(article.created_at)

    updated_at_str = ""
    if article.updated_at is not None:
        if hasattr(article.updated_at, "isoformat"):
            updated_at_str = article.updated_at.isoformat()
        else:
            updated_at_str = str(article.updated_at)

    return ArticleOut(
        slug=getattr(article, "slug", ""),
        title=getattr(article, "title", ""),
        description=getattr(article, "description", ""),
        body=getattr(article, "body", ""),
        tagList=getattr(article, "tagList", []) or [],
        createdAt=created_at_str,
        updatedAt=updated_at_str,
        favorited=favorited_bool,
        favoritesCount=favorites_count,
        author=author_data,
    )


async def _batch_fetch_authors(session: AsyncSession, articles: list[Article]) -> dict[int, User]:
    author_ids = {article.author_id for article in articles if article.author_id is not None}
    authors: dict[int, User] = {}
    if author_ids:
        # Use session.get to fetch User objects directly
        for author_id in author_ids:
            user = await session.get(User, author_id)
            if user:
                authors[author_id] = user
    return authors


async def _batch_fetch_following_map(
    session: AsyncSession, follower_id: int | None, author_ids: list[int]
) -> dict[int, bool]:
    following_map: dict[int, bool] = {}
    if follower_id and author_ids:
        from app.domain.users.orm import follower_table

        result = await session.execute(
            select(follower_table.c.followee_id).where(
                (follower_table.c.follower_id == follower_id)
                & (follower_table.c.followee_id.in_(author_ids))
            )
        )
        for row in result.scalars().all():
            following_map[row] = True
    return following_map


async def _build_favorited_map(
    session: AsyncSession, follower_id: int, article_ids: list[int]
) -> dict[int, bool]:
    """Return a map of article_id to True if favorited by follower_id."""
    favorited_map: dict[int, bool] = {}
    if follower_id and article_ids:
        result = await session.execute(
            select(article_favorite_table.c.article_id).where(
                (article_favorite_table.c.user_id == follower_id)
                & (article_favorite_table.c.article_id.in_(article_ids))
            )
        )
        for row in result.scalars().all():
            favorited_map[row] = True
    return favorited_map


def _build_articles_list(
    articles: list[Article],
    authors: dict[int, User],
    following_map: dict[int, bool],
    favorited_map: dict[int, bool],
    favorites_count_map: dict[int, int],
    follower_id: int,
) -> list[dict]:
    """
    Build a list of article response dictionaries with author and relationship data.

    Args:
        articles: List of article domain models
        authors: Map of author_id to User objects
        following_map: Map of author_id to following status
        favorited_map: Map of article_id to favorited status
        favorites_count_map: Map of article_id to favorites count
        follower_id: ID of the current user (for following logic)

    Returns:
        List of article response dictionaries
    """
    articles_list: list[dict] = []
    for article in articles:
        author_obj = authors.get(article.author_id)
        following = False
        author_id = author_obj.id if author_obj and author_obj.id is not None else None
        if follower_id and author_obj and author_id is not None and author_id != follower_id:
            following = following_map.get(author_id, False)
        article_id: int = article.id if article.id is not None else -1
        favorited: bool = favorited_map.get(int(article_id), False)
        favorites_count: int = favorites_count_map.get(int(article_id), 0)
        article_out = _build_article_response(
            article, author_obj, following, favorited=favorited, favorites_count=favorites_count
        )
        articles_list.append(article_out.model_dump())
    return articles_list


@transactional()
async def list_articles(
    uow: AsyncUnitOfWork,
    tag: str | None = None,
    author: str | None = None,
    favorited_by: str | None = None,
    limit: int = 20,
    offset: int = 0,
    current_user: UserWithToken | None = None,
) -> dict:
    """List articles with filters and pagination using SQLAlchemy models."""
    repo = ArticleRepository(uow.session)
    user_repo = UserRepository(uow.session)
    author_id = None
    if author:
        author_obj = await user_repo.get_by_username_or_email(username=author, email="")
        if author_obj:
            author_id = author_obj.id
    favorited_user_id = None
    if favorited_by:
        favorited_user = await user_repo.get_by_username_or_email(username=favorited_by, email="")
        if not favorited_user:
            favorited_user_id = -1
        else:
            favorited_user_id = favorited_user.id
    articles, total = await repo.list_articles(
        tag=tag, author_id=author_id, favorited_by=favorited_user_id, offset=offset, limit=limit
    )
    follower_id = current_user.id if current_user else -1
    authors = await _batch_fetch_authors(uow.session, list(articles))
    following_map = await _batch_fetch_following_map(uow.session, follower_id, list(authors.keys()))
    article_ids = [a.id for a in articles if a.id is not None]
    favorites_count_map = await repo.get_favorites_count(article_ids)
    favorited_map = await _build_favorited_map(uow.session, follower_id, article_ids)
    articles_list = _build_articles_list(
        list(articles), authors, following_map, favorited_map, favorites_count_map, follower_id
    )
    return {"articles": articles_list, "articlesCount": total}


@transactional()
async def create_article(
    uow: AsyncUnitOfWork, article: "ArticleCreate", user: UserWithToken
) -> dict:
    """Create a new article using SQLAlchemy models and publish an event."""
    repo = ArticleRepository(uow.session)
    now = datetime.now(timezone.utc).replace(tzinfo=None)  # ensure naive UTC
    base_slug = slugify(article.title)
    slug = base_slug
    # Ensure slug uniqueness
    existing = await repo.get_by_slug(slug)
    if existing:
        slug = f"{base_slug}-{secrets.token_hex(4)}"
    db_article = Article(
        title=article.title,
        description=article.description,
        body=article.body,
        author_id=user.id,
    )
    db_article.slug = slug
    db_article.tagList = article.tagList or []
    db_article.created_at = now
    db_article.updated_at = now
    created = await repo.add(db_article)
    # Publish event
    if created.id is not None:
        shared_event_bus.publish(ArticleCreated(article_id=created.id, author_id=user.id))
    # Always not favorited and 0 count on creation
    # Fetch author as SQLAlchemy User
    author_obj = await uow.session.get(User, user.id)
    article_out = _build_article_response(
        created, author_obj, following=False, favorited=False, favorites_count=0
    )
    return {"article": article_out.model_dump()}


@transactional()
async def feed_articles(
    uow: AsyncUnitOfWork,
    current_user: UserWithToken,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """Get articles from users that the current user follows."""
    repo = ArticleRepository(uow.session)

    articles, total = await repo.feed_articles(
        follower_id=current_user.id, offset=offset, limit=limit
    )

    # Build the response using existing helper functions
    follower_id = current_user.id
    authors = await _batch_fetch_authors(uow.session, list(articles))
    following_map = await _batch_fetch_following_map(uow.session, follower_id, list(authors.keys()))
    article_ids = [a.id for a in articles if a.id is not None]
    favorites_count_map = await repo.get_favorites_count(article_ids)
    favorited_map = await _build_favorited_map(uow.session, follower_id, article_ids)

    articles_list = _build_articles_list(
        list(articles), authors, following_map, favorited_map, favorites_count_map, follower_id
    )

    return {"articles": articles_list, "articlesCount": total}


@transactional()
async def get_article_by_slug(
    uow: AsyncUnitOfWork, slug: str, current_user: UserWithToken | None = None
) -> dict:
    """
    Get a single article by slug.

    Args:
        slug: The article slug
        current_user: Optional current user for following/favorited status

    Returns:
        dict: Article data with author, favorited, and following status

    Raises:
        ArticleNotFoundError: If article with slug doesn't exist
    """
    repo = ArticleRepository(uow.session)
    user_repo = UserRepository(uow.session)

    # Get the article
    article = await repo.get_by_slug(slug)
    if not article:
        raise ArticleNotFoundError(f"Article with slug '{slug}' not found")

    # Get the article author
    author = await user_repo.get_by_id(article.author_id) if article.author_id else None

    # Determine following status
    following = False
    favorited = False
    current_user_id = None

    if current_user and author and author.id:
        current_user_id = current_user.id
        following = await user_repo.is_following(current_user.id, author.id)

    # Check if current user favorited this article
    if current_user_id and article.id:
        favorited_map = await _build_favorited_map(uow.session, current_user_id, [article.id])
        favorited = favorited_map.get(article.id, False)

    # Get favorites count
    favorites_count = 0
    if article.id:
        favorites_count_map = await repo.get_favorites_count([article.id])
        favorites_count = favorites_count_map.get(article.id, 0)

    # Build response
    article_out = _build_article_response(
        article=article,
        author_obj=author,
        following=following,
        favorited=favorited,
        favorites_count=favorites_count,
    )

    return {"article": article_out.model_dump()}


@transactional()
async def update_article(
    uow: AsyncUnitOfWork, slug: str, article_update: ArticleUpdate, current_user: UserWithToken
) -> dict:
    """
    Update an existing article by slug and publish an event.

    Args:
        slug: The slug of the article to update
        article_update: The update data for the article
        current_user: The currently authenticated user

    Returns:
        Dictionary containing the updated article data

    Raises:
        ArticleNotFoundError: If the article doesn't exist
        ArticlePermissionError: If user is not the author
    """
    from slugify import slugify

    repo = ArticleRepository(uow.session)
    user_repo = UserRepository(uow.session)

    # Get the existing article
    article = await repo.get_by_slug(slug)
    if not article:
        raise ArticleNotFoundError(f"Article with slug '{slug}' not found")

    # Check if current user is the author
    if article.author_id != current_user.id:
        raise ArticlePermissionError("Not authorized to update this article")

    # Update only provided fields
    updated = False
    updated_fields = []

    if article_update.title is not None and article_update.title != article.title:
        article.title = article_update.title
        updated_fields.append("title")
        # Generate new slug if title changed
        new_slug = slugify(article_update.title)
        # Ensure slug uniqueness
        while await repo.get_by_slug(new_slug):
            random_suffix = secrets.token_hex(4)
            new_slug = f"{slugify(article_update.title)}-{random_suffix}"
        article.slug = new_slug
        updated_fields.append("slug")
        updated = True

    if article_update.description is not None and article_update.description != article.description:
        article.description = article_update.description
        updated_fields.append("description")
        updated = True

    if article_update.body is not None and article_update.body != article.body:
        article.body = article_update.body
        updated_fields.append("body")
        updated = True

    # Update timestamp if any changes were made
    if updated:
        article.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    # Save the updated article
    updated_article = await repo.update(article)

    # Publish article update event
    if updated and updated_article.id is not None:
        shared_event_bus.publish(
            ArticleUpdated(
                article_id=updated_article.id,
                author_id=current_user.id,
                updated_fields=updated_fields,
            )
        )

    # Get author information
    author = await user_repo.get_by_id(updated_article.author_id)

    # Determine following status (always False since user is updating their own article)
    following = False
    favorited = False

    # Check if current user favorited this article
    if updated_article.id:
        favorited_map = await _build_favorited_map(
            uow.session, current_user.id, [updated_article.id]
        )
        favorited = favorited_map.get(updated_article.id, False)

    # Get favorites count
    favorites_count = 0
    if updated_article.id:
        favorites_count_map = await repo.get_favorites_count([updated_article.id])
        favorites_count = favorites_count_map.get(updated_article.id, 0)

    # Build response
    article_out = _build_article_response(
        article=updated_article,
        author_obj=author,
        following=following,
        favorited=favorited,
        favorites_count=favorites_count,
    )

    return {"article": article_out.model_dump()}


@transactional()
async def delete_article(uow: AsyncUnitOfWork, slug: str, current_user: UserWithToken) -> None:
    """
    Delete an article by slug and publish an event.

    Only the author of the article can delete it.

    Args:
        slug: The slug of the article to delete
        current_user: The authenticated user

    Raises:
        ArticleNotFoundError: If the article doesn't exist
        ArticlePermissionError: If the user is not the author
    """
    repo = ArticleRepository(uow.session)
    # Find the article
    article = await repo.get_by_slug(slug)
    if not article:
        raise ArticleNotFoundError(f"Article with slug '{slug}' not found")
    # Check permission - only author can delete
    if article.author_id != current_user.id:
        raise ArticlePermissionError("Only the author can delete this article")
    # Delete the article
    await repo.delete(article)
    # Publish event
    if article.id is not None:
        shared_event_bus.publish(ArticleDeleted(article_id=article.id, author_id=current_user.id))


@transactional()
async def favorite_article(uow: AsyncUnitOfWork, slug: str, current_user: UserWithToken) -> dict:
    """
    Add an article to user's favorites and publish an event.

    Args:
        slug: The slug of the article to favorite
        current_user: The authenticated user

    Returns:
        Article response with updated favorite status

    Raises:
        ArticleNotFoundError: If the article doesn't exist
    """
    repo = ArticleRepository(uow.session)
    user_repo = UserRepository(uow.session)
    # Find the article
    article = await repo.get_by_slug(slug)
    if not article:
        raise ArticleNotFoundError(f"Article with slug '{slug}' not found")
    # Add to favorites
    if article.id is not None:
        await repo.add_favorite(article.id, current_user.id)
        shared_event_bus.publish(ArticleFavorited(article_id=article.id, user_id=current_user.id))
    # Get updated article data with author info
    author = None
    if article.author_id:
        author = await user_repo.get_by_id(article.author_id)

    # Check if current user is following the author
    following = False
    if author and author.id is not None and author.id != current_user.id:
        following = await user_repo.is_following(current_user.id, author.id)

    # Get updated favorite status and count
    favorited = True  # Just favorited
    favorites_count = 0
    if article.id is not None:
        counts = await repo.get_favorites_count([article.id])
        favorites_count = counts.get(article.id, 0)

    article_out = _build_article_response(
        article=article,
        author_obj=author,
        following=following,
        favorited=favorited,
        favorites_count=favorites_count,
    )

    return {"article": article_out.model_dump()}


@transactional()
async def unfavorite_article(uow: AsyncUnitOfWork, slug: str, current_user: UserWithToken) -> dict:
    """
    Remove an article from user's favorites and publish an event.

    Args:
        slug: The slug of the article to unfavorite
        current_user: The authenticated user

    Returns:
        Article response with updated favorite status

    Raises:
        ArticleNotFoundError: If the article doesn't exist
    """
    repo = ArticleRepository(uow.session)
    user_repo = UserRepository(uow.session)
    # Find the article
    article = await repo.get_by_slug(slug)
    if not article:
        raise ArticleNotFoundError(f"Article with slug '{slug}' not found")
    # Remove from favorites
    if article.id is not None:
        await repo.remove_favorite(article.id, current_user.id)
        shared_event_bus.publish(ArticleUnfavorited(article_id=article.id, user_id=current_user.id))
    # Get updated article data with author info
    author = None
    if article.author_id:
        author = await user_repo.get_by_id(article.author_id)

    # Check if current user is following the author
    following = False
    if author and author.id is not None and author.id != current_user.id:
        following = await user_repo.is_following(current_user.id, author.id)

    # Get updated favorite status and count
    favorited = False  # Just unfavorited
    favorites_count = 0
    if article.id is not None:
        counts = await repo.get_favorites_count([article.id])
        favorites_count = counts.get(article.id, 0)

    article_out = _build_article_response(
        article=article,
        author_obj=author,
        following=following,
        favorited=favorited,
        favorites_count=favorites_count,
    )

    return {"article": article_out.model_dump()}
