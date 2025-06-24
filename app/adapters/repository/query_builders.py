"""
Query builders for complex database queries.

This module provides reusable query builders that eliminate
code duplication and follow the Builder pattern.
"""

from sqlalchemy import func, select
from sqlalchemy.sql import Select

from app.domain.articles.orm import Article, article_favorite_table, article_table


class ArticleQueryBuilder:
    """
    Builder for article queries following the Builder pattern.

    Eliminates code duplication in filtering and pagination logic.
    """

    def __init__(self) -> None:
        """Initialize builder with base query."""
        self._query = select(Article)
        self._count_query = select(func.count()).select_from(article_table)

    def with_tag(self, tag: str) -> "ArticleQueryBuilder":
        """Filter articles by tag."""
        condition = article_table.c.tagList.op("@>")([tag])
        self._query = self._query.where(condition)
        self._count_query = self._count_query.where(condition)
        return self

    def with_author(self, author_id: int) -> "ArticleQueryBuilder":
        """Filter articles by author."""
        condition = article_table.c.author_id == author_id
        self._query = self._query.where(condition)
        self._count_query = self._count_query.where(condition)
        return self

    def favorited_by(self, user_id: int) -> "ArticleQueryBuilder":
        """Filter articles favorited by user."""
        subq = select(article_favorite_table.c.article_id).where(
            article_favorite_table.c.user_id == user_id
        )
        condition = article_table.c.id.in_(subq)
        self._query = self._query.where(condition)
        self._count_query = self._count_query.where(condition)
        return self

    def authored_by_followed_users(self, follower_id: int) -> "ArticleQueryBuilder":
        """Filter articles by users that follower_id follows."""
        from app.domain.users.orm import follower_table

        followed_users_subquery = select(follower_table.c.followee_id).where(
            follower_table.c.follower_id == follower_id
        )
        condition = article_table.c.author_id.in_(followed_users_subquery)
        self._query = self._query.where(condition)
        self._count_query = self._count_query.where(condition)
        return self

    def ordered_by_created_desc(self) -> "ArticleQueryBuilder":
        """Order articles by creation date descending."""
        self._query = self._query.order_by(article_table.c.created_at.desc())
        return self

    def paginated(self, offset: int = 0, limit: int = 20) -> "ArticleQueryBuilder":
        """Apply pagination to the query."""
        self._query = self._query.offset(offset).limit(limit)
        return self

    def build(self) -> Select:
        """Build and return the final query."""
        return self._query

    def build_count_query(self) -> Select:
        """Build and return the count query."""
        return self._count_query
