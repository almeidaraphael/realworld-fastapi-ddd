"""
Article response builder service.

This module centralizes article response building logic to reduce
code duplication across article services.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repository.articles import ArticleRepository
from app.adapters.repository.users import UserRepository
from app.domain.articles.orm import Article
from app.domain.users.schemas import UserWithToken
from app.service_layer.articles.services import (
    _build_article_response,
    _build_favorited_map,
)


class ArticleResponseBuilder:
    """
    Service to build consistent article responses.

    Centralizes the logic for fetching and building article responses
    with author information, following status, and favorite status.
    """

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
        self.article_repo = ArticleRepository(session)
        self.user_repo = UserRepository(session)

    async def build_single_article_response(
        self,
        article: Article,
        current_user: UserWithToken | None = None,
    ) -> dict:
        """
        Build a complete article response with author and relationship data.

        Args:
            article: The article domain model
            current_user: The current authenticated user (optional)

        Returns:
            Dictionary containing the article response
        """
        # Get author information
        author = None
        if article.author_id:
            author = await self.user_repo.get_by_id(article.author_id)

        # Determine following status
        following = False
        if current_user and author and author.id is not None and author.id != current_user.id:
            following = await self.user_repo.is_following(current_user.id, author.id)

        # Check if current user favorited this article
        favorited = False
        if current_user and article.id:
            favorited_map = await _build_favorited_map(self.session, current_user.id, [article.id])
            favorited = favorited_map.get(article.id, False)

        # Get favorites count
        favorites_count = 0
        if article.id:
            favorites_count_map = await self.article_repo.get_favorites_count([article.id])
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

    async def build_article_response_after_favorite(
        self,
        article: Article,
        current_user: UserWithToken,
        favorited: bool,
    ) -> dict:
        """
        Build article response after favorite/unfavorite operation.

        Args:
            article: The article domain model
            current_user: The current authenticated user
            favorited: Whether the article is now favorited

        Returns:
            Dictionary containing the article response
        """
        # Get author information
        author = None
        if article.author_id:
            author = await self.user_repo.get_by_id(article.author_id)

        # Check if current user is following the author
        following = False
        if author and author.id is not None and author.id != current_user.id:
            following = await self.user_repo.is_following(current_user.id, author.id)

        # Get updated favorites count
        favorites_count = 0
        if article.id is not None:
            counts = await self.article_repo.get_favorites_count([article.id])
            favorites_count = counts.get(article.id, 0)

        article_out = _build_article_response(
            article=article,
            author_obj=author,
            following=following,
            favorited=favorited,
            favorites_count=favorites_count,
        )

        return {"article": article_out.model_dump()}
