from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.articles.orm import Article, ArticleFavorite, article_favorite_table, article_table


class ArticleRepository:
    """
    Repository for article data access operations.

    Provides methods for CRUD operations on articles including
    listing with filters, favorites management, and persistence.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def add(self, article: Article) -> Article:
        """Add a new article to the database."""
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        return article

    async def get_by_slug(self, slug: str) -> Article | None:
        """Get an article by its slug."""
        result = await self.session.execute(select(Article).where(article_table.c.slug == slug))
        return result.scalars().first()

    async def update(self, article: Article) -> Article:
        """Update an existing article in the database."""
        await self.session.commit()
        await self.session.refresh(article)
        return article

    async def list_articles(
        self,
        *,
        tag: str | None = None,
        author_id: int | None = None,
        favorited_by: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Article], int]:
        """
        List articles with optional filters and pagination.

        Args:
            tag: Filter by tag (optional)
            author_id: Filter by author ID (optional)
            favorited_by: Filter by user who favorited (optional)
            offset: Pagination offset
            limit: Pagination limit

        Returns:
            Tuple of (articles list, total count)
        """
        query = select(Article)
        if tag:
            query = query.where(article_table.c.tagList.op("@>")([tag]))
        if author_id:
            query = query.where(article_table.c.author_id == author_id)
        if favorited_by is not None:
            subq = select(article_favorite_table.c.article_id).where(
                article_favorite_table.c.user_id == favorited_by
            )
            query = query.where(article_table.c.id.in_(subq))
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        articles = list(result.scalars().all())

        count_query = select(func.count()).select_from(article_table)
        if tag:
            count_query = count_query.where(article_table.c.tagList.op("@>")([tag]))
        if author_id:
            count_query = count_query.where(article_table.c.author_id == author_id)
        if favorited_by is not None:
            subq = select(article_favorite_table.c.article_id).where(
                article_favorite_table.c.user_id == favorited_by
            )
            count_query = count_query.where(article_table.c.id.in_(subq))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return articles, total

    async def get_favorites_count(self, article_ids: list[int]) -> dict[int, int]:
        """Get the count of favorites for a list of articles.

        Args:
            article_ids: List of article IDs to get favorite counts for

        Returns:
            Dictionary mapping article_id to favorite count
        """
        if not article_ids:
            return {}
        result = await self.session.execute(
            select(
                article_favorite_table.c.article_id, func.count(article_favorite_table.c.user_id)
            )
            .where(article_favorite_table.c.article_id.in_(article_ids))
            .group_by(article_favorite_table.c.article_id)
        )
        return {row[0]: row[1] for row in result.all()}

    async def is_favorited_by(self, article_id: int, user_id: int) -> bool:
        """Check if an article is favorited by a specific user."""
        result = await self.session.execute(
            select(ArticleFavorite).where(
                and_(
                    article_favorite_table.c.article_id == article_id,
                    article_favorite_table.c.user_id == user_id,
                )
            )
        )
        return result.scalars().first() is not None

    async def feed_articles(
        self,
        *,
        follower_id: int,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Article], int]:
        """
        Get articles from users that the given user follows.

        Args:
            follower_id: ID of the user whose feed to get
            offset: Pagination offset
            limit: Pagination limit

        Returns:
            Tuple of (articles list, total count)
        """
        from app.domain.users.orm import follower_table

        # Get articles from users that follower_id follows
        followed_users_subquery = select(follower_table.c.followee_id).where(
            follower_table.c.follower_id == follower_id
        )

        query = (
            select(Article)
            .where(article_table.c.author_id.in_(followed_users_subquery))
            .order_by(article_table.c.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)
        articles = list(result.scalars().all())

        # Count total articles in feed
        count_query = (
            select(func.count())
            .select_from(article_table)
            .where(article_table.c.author_id.in_(followed_users_subquery))
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        return articles, total

    async def delete(self, article: Article) -> None:
        """Delete an article from the database."""
        await self.session.delete(article)
        await self.session.commit()

    async def add_favorite(self, article_id: int, user_id: int) -> None:
        """Add an article to user's favorites."""
        # Check if already favorited
        existing = await self.session.execute(
            select(ArticleFavorite).where(
                and_(
                    article_favorite_table.c.article_id == article_id,
                    article_favorite_table.c.user_id == user_id,
                )
            )
        )
        if existing.scalars().first() is None:
            favorite = ArticleFavorite(article_id=article_id, user_id=user_id)
            self.session.add(favorite)
            await self.session.commit()

    async def remove_favorite(self, article_id: int, user_id: int) -> None:
        """Remove an article from user's favorites."""
        result = await self.session.execute(
            select(ArticleFavorite).where(
                and_(
                    article_favorite_table.c.article_id == article_id,
                    article_favorite_table.c.user_id == user_id,
                )
            )
        )
        favorite = result.scalars().first()
        if favorite:
            await self.session.delete(favorite)
            await self.session.commit()
