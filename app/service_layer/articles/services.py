import secrets
from datetime import datetime, timezone

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.adapters.repository.articles import ArticleRepository
from app.adapters.repository.users import UserRepository
from app.domain.articles.orm import Article, article_favorite_table
from app.domain.articles.schemas import ArticleAuthorOut, ArticleCreate, ArticleOut
from app.domain.users.orm import User
from app.domain.users.schemas import UserWithToken


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


async def list_articles(
    tag: str | None = None,
    author: str | None = None,
    favorited_by: str | None = None,
    limit: int = 20,
    offset: int = 0,
    current_user: UserWithToken | None = None,
    uow_factory: type[AsyncUnitOfWork] = AsyncUnitOfWork,
) -> dict:
    """List articles with filters and pagination using SQLAlchemy models."""
    async with uow_factory() as uow:
        repo = ArticleRepository(uow.session)
        user_repo = UserRepository(uow.session)
        author_id = None
        if author:
            author_obj = await user_repo.get_by_username_or_email(username=author, email="")
            if author_obj:
                author_id = author_obj.id
        favorited_user_id = None
        if favorited_by:
            favorited_user = await user_repo.get_by_username_or_email(
                username=favorited_by, email=""
            )
            if not favorited_user:
                favorited_user_id = -1
            else:
                favorited_user_id = favorited_user.id
        articles, total = await repo.list_articles(
            tag=tag, author_id=author_id, favorited_by=favorited_user_id, offset=offset, limit=limit
        )
        follower_id = current_user.id if current_user else -1
        authors = await _batch_fetch_authors(uow.session, list(articles))
        following_map = await _batch_fetch_following_map(
            uow.session, follower_id, list(authors.keys())
        )
        article_ids = [a.id for a in articles if a.id is not None]
        favorites_count_map = await repo.get_favorites_count(article_ids)
        favorited_map = await _build_favorited_map(uow.session, follower_id, article_ids)
        articles_list = _build_articles_list(
            list(articles), authors, following_map, favorited_map, favorites_count_map, follower_id
        )
        return {"articles": articles_list, "articlesCount": total}


async def create_article(article: "ArticleCreate", user: UserWithToken) -> dict:
    """Create a new article using SQLAlchemy models."""
    async with AsyncUnitOfWork() as uow:
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
        # Always not favorited and 0 count on creation
        # Fetch author as SQLAlchemy User
        author_obj = await uow.session.get(User, user.id)
        article_out = _build_article_response(
            created, author_obj, following=False, favorited=False, favorites_count=0
        )
        return {"article": article_out.model_dump()}
