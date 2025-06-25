"""
Service layer for comment operations.

This module contains business logic for comment management,
including creation, retrieval, and deletion of comments.
"""

from datetime import datetime, timezone

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.adapters.repository.articles import ArticleRepository
from app.adapters.repository.comments import CommentRepository
from app.adapters.repository.users import UserRepository
from app.domain.articles.exceptions import ArticleNotFoundError
from app.domain.comments.exceptions import CommentNotFoundError, CommentPermissionError
from app.domain.comments.models import Comment
from app.domain.comments.schemas import CommentAuthor, CommentCreate, CommentOut
from app.domain.users.exceptions import UserNotFoundError
from app.events import ArticleCommentAdded, CommentDeleted, shared_event_bus
from app.shared.transaction import TransactionalService, transactional


def _build_comment_response(
    comment: Comment,
    author_username: str,
    author_bio: str = "",
    author_image: str = "",
    following: bool = False,
) -> CommentOut:
    """Build comment response from domain model."""
    return CommentOut(
        id=comment.id or 0,
        createdAt=comment.created_at or "",
        updatedAt=comment.updated_at or "",
        body=comment.body,
        author=CommentAuthor(
            username=author_username,
            bio=author_bio,
            image=author_image,
            following=following,
        ),
    )


class CommentService(TransactionalService):
    """Service for comment business logic with enhanced transaction management."""

    @transactional()
    async def add_comment_to_article(
        self,
        uow: AsyncUnitOfWork,
        article_slug: str,
        comment_data: CommentCreate,
        current_user_id: int,
    ) -> CommentOut:
        """Add a new comment to an article and publish an event."""
        # Get repositories
        article_repo = ArticleRepository(uow.session)
        comment_repo = CommentRepository(uow.session)
        user_repo = UserRepository(uow.session)

        # Check if article exists
        article = await article_repo.get_by_slug(article_slug)
        if not article or article.id is None:
            raise ArticleNotFoundError(f"Article with slug '{article_slug}' not found")

        # Get current user
        current_user = await user_repo.get_by_id(current_user_id)
        if not current_user:
            raise UserNotFoundError("Current user not found")

        # Create comment
        now = datetime.now(timezone.utc).isoformat()
        comment = Comment(
            body=comment_data.body,
            article_id=article.id,
            author_id=current_user_id,
            created_at=now,
            updated_at=now,
        )

        # Save comment
        saved_comment = await comment_repo.add(comment)

        # Publish async event for background processing
        await shared_event_bus.publish_async(
            ArticleCommentAdded(
                article_id=article.id,
                comment_id=saved_comment.id or 0,
                author_id=current_user_id,
            )
        )

        # Build response
        return _build_comment_response(
            comment=saved_comment,
            author_username=current_user.username,
            author_bio=current_user.bio or "",
            author_image=current_user.image or "",
            following=False,  # User can't follow themselves
        )

    @transactional()
    async def get_comments_from_article(
        self, uow: AsyncUnitOfWork, article_slug: str, current_user_id: int | None = None
    ) -> list[CommentOut]:
        """Get all comments for an article."""
        # Get repositories
        article_repo = ArticleRepository(uow.session)
        comment_repo = CommentRepository(uow.session)
        user_repo = UserRepository(uow.session)

        # Check if article exists
        article = await article_repo.get_by_slug(article_slug)
        if not article or article.id is None:
            raise ArticleNotFoundError(f"Article with slug '{article_slug}' not found")

        # Get comments
        comments = await comment_repo.list_by_article_id(article.id)

        # Build responses
        comment_responses = []
        for comment in comments:
            # Get comment author
            author = await user_repo.get_by_id(comment.author_id)
            if not author:
                continue  # Skip comments with missing authors

            # Check if current user follows the author
            following = False
            if current_user_id and current_user_id != comment.author_id:
                current_user = await user_repo.get_by_id(current_user_id)
                if current_user and author.id is not None:
                    following = await user_repo.is_following(
                        follower_id=current_user_id, followee_id=author.id
                    )

            comment_response = _build_comment_response(
                comment=comment,
                author_username=author.username,
                author_bio=author.bio or "",
                author_image=author.image or "",
                following=following,
            )
            comment_responses.append(comment_response)

        return comment_responses

    @transactional()
    async def delete_comment(
        self, uow: AsyncUnitOfWork, article_slug: str, comment_id: int, current_user_id: int
    ) -> None:
        """Delete a comment from an article and publish an event."""
        # Get repositories
        article_repo = ArticleRepository(uow.session)
        comment_repo = CommentRepository(uow.session)

        # Check if article exists
        article = await article_repo.get_by_slug(article_slug)
        if not article:
            raise ArticleNotFoundError(f"Article with slug '{article_slug}' not found")

        # Get comment
        comment = await comment_repo.get_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError(f"Comment with id {comment_id} not found")

        # Check if comment belongs to the article
        if comment.article_id != article.id:
            raise CommentNotFoundError(f"Comment with id {comment_id} not found")

        # Check permission - only comment author can delete
        if comment.author_id != current_user_id:
            raise CommentPermissionError("You can only delete your own comments")

        # Delete comment
        await comment_repo.delete(comment)

        # Publish comment deletion event
        if comment.id is not None and article.id is not None:
            await shared_event_bus.publish_async(
                CommentDeleted(
                    comment_id=comment.id,
                    article_id=article.id,
                    author_id=comment.author_id,
                )
            )


# Keep original class for backward compatibility during migration
class CommentServiceOriginal:
    """Original CommentService class - kept for backward compatibility."""

    def __init__(self, uow: AsyncUnitOfWork):
        """Initialize service with unit of work."""
        self.uow = uow

    async def add_comment_to_article(
        self, article_slug: str, comment_data: CommentCreate, current_user_id: int
    ) -> CommentOut:
        """Add a new comment to an article and publish an event."""
        async with self.uow:
            # Get repositories
            article_repo = ArticleRepository(self.uow.session)
            comment_repo = CommentRepository(self.uow.session)
            user_repo = UserRepository(self.uow.session)

            # Check if article exists
            article = await article_repo.get_by_slug(article_slug)
            if not article or article.id is None:
                raise ArticleNotFoundError(f"Article with slug '{article_slug}' not found")

            # Get current user
            current_user = await user_repo.get_by_id(current_user_id)
            if not current_user:
                raise UserNotFoundError("Current user not found")

            # Create comment
            now = datetime.now(timezone.utc).isoformat()
            comment = Comment(
                body=comment_data.body,
                article_id=article.id,
                author_id=current_user_id,
                created_at=now,
                updated_at=now,
            )

            # Save comment
            saved_comment = await comment_repo.add(comment)

            # Publish domain event (sync)
            shared_event_bus.publish(
                ArticleCommentAdded(
                    article_id=article.id,
                    comment_id=saved_comment.id or 0,
                    author_id=current_user_id,
                )
            )

            # Publish async event for background processing
            await shared_event_bus.publish_async(
                ArticleCommentAdded(
                    article_id=article.id,
                    comment_id=saved_comment.id or 0,
                    author_id=current_user_id,
                )
            )

            # Build response
            return _build_comment_response(
                comment=saved_comment,
                author_username=current_user.username,
                author_bio=current_user.bio or "",
                author_image=current_user.image or "",
                following=False,  # User can't follow themselves
            )
