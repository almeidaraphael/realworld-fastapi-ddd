"""
Enhanced comment service demonstrating TransactionalService usage.

This module shows how to use the TransactionalService base class
for consistent transaction management in service classes.
"""

from collections.abc import Awaitable, Callable
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


class EnhancedCommentService(TransactionalService):
    """
    Enhanced comment service using TransactionalService base class.

    This service demonstrates how to use the TransactionalService base class
    for consistent transaction management across all service methods.
    """

    @transactional()
    async def add_comment_to_article(
        self,
        uow: AsyncUnitOfWork,
        article_slug: str,
        comment_data: CommentCreate,
        current_user_id: int,
    ) -> CommentOut:
        """Add a new comment to an article with transaction management."""
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
            saved_comment,
            author_username=current_user.username,
            author_bio=current_user.bio or "",
            author_image=current_user.image or "",
            following=False,  # Could implement following logic
        )

    @transactional()
    async def get_comments_for_article(
        self,
        uow: AsyncUnitOfWork,
        article_slug: str,
        current_user_id: int | None = None,
    ) -> list[CommentOut]:
        """Get all comments for an article with author information."""
        # Get repositories
        article_repo = ArticleRepository(uow.session)
        comment_repo = CommentRepository(uow.session)
        user_repo = UserRepository(uow.session)

        # Check if article exists
        article = await article_repo.get_by_slug(article_slug)
        if not article or article.id is None:
            raise ArticleNotFoundError(f"Article with slug '{article_slug}' not found")

        # Get comments for the article
        comments = await comment_repo.list_by_article_id(article.id)

        # Build responses with author information
        comment_responses = []
        for comment in comments:
            # Get author information
            author = await user_repo.get_by_id(comment.author_id)
            if author:
                # TODO: Implement following logic if current_user_id is provided
                following = False
                comment_response = _build_comment_response(
                    comment,
                    author_username=author.username,
                    author_bio=author.bio or "",
                    author_image=author.image or "",
                    following=following,
                )
                comment_responses.append(comment_response)

        return comment_responses

    @transactional()
    async def delete_comment(
        self,
        uow: AsyncUnitOfWork,
        article_slug: str,
        comment_id: int,
        current_user_id: int,
    ) -> None:
        """Delete a comment if the current user is the author."""
        # Get repositories
        article_repo = ArticleRepository(uow.session)
        comment_repo = CommentRepository(uow.session)

        # Check if article exists
        article = await article_repo.get_by_slug(article_slug)
        if not article or article.id is None:
            raise ArticleNotFoundError(f"Article with slug '{article_slug}' not found")

        # Get the comment
        comment = await comment_repo.get_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError(f"Comment with ID {comment_id} not found")

        # Check if comment belongs to the article
        if comment.article_id != article.id:
            raise CommentNotFoundError("Comment does not belong to this article")

        # Check if current user is the author
        if comment.author_id != current_user_id:
            raise CommentPermissionError("Only the comment author can delete this comment")

        # Delete the comment
        await comment_repo.delete(comment)

        # Publish deletion event
        shared_event_bus.publish(
            CommentDeleted(
                comment_id=comment_id,
                article_id=article.id,
                author_id=current_user_id,
            )
        )

    async def bulk_add_comments(
        self,
        article_slug: str,
        comments_data: list[tuple[CommentCreate, int]],  # (comment_data, user_id)
    ) -> list[CommentOut]:
        """
        Example of using BulkTransactionManager for multiple operations.

        This method demonstrates how to use the bulk transaction manager
        for operations that need to succeed or fail together.
        """
        from app.shared.transaction import BulkTransactionManager

        manager = BulkTransactionManager()

        # Add each comment operation to the bulk manager
        for comment_data, user_id in comments_data:

            def create_operation(
                cd: CommentCreate, uid: int
            ) -> Callable[[AsyncUnitOfWork], Awaitable[CommentOut]]:
                async def operation(uow: AsyncUnitOfWork) -> CommentOut:
                    return await self._add_single_comment(uow, article_slug, cd, uid)

                return operation

            manager.add_operation(create_operation(comment_data, user_id))

        # Execute all operations in a single transaction
        results = await manager.execute_all()
        return results

    async def _add_single_comment(
        self,
        uow: AsyncUnitOfWork,
        article_slug: str,
        comment_data: CommentCreate,
        user_id: int,
    ) -> CommentOut:
        """Helper method for bulk comment creation."""
        # This uses the existing add_comment_to_article logic
        # but without the @transactional decorator since it's called
        # from within a bulk transaction
        article_repo = ArticleRepository(uow.session)
        comment_repo = CommentRepository(uow.session)
        user_repo = UserRepository(uow.session)

        article = await article_repo.get_by_slug(article_slug)
        if not article or article.id is None:
            raise ArticleNotFoundError(f"Article with slug '{article_slug}' not found")

        current_user = await user_repo.get_by_id(user_id)
        if not current_user:
            raise UserNotFoundError("User not found")

        now = datetime.now(timezone.utc).isoformat()
        comment = Comment(
            body=comment_data.body,
            article_id=article.id,
            author_id=user_id,
            created_at=now,
            updated_at=now,
        )

        saved_comment = await comment_repo.add(comment)

        return _build_comment_response(
            saved_comment,
            author_username=current_user.username,
            author_bio=current_user.bio or "",
            author_image=current_user.image or "",
            following=False,
        )

    async def safe_get_comment(self, article_slug: str, comment_id: int) -> CommentOut | None:
        """
        Example of using _execute_in_transaction for safe operations.

        This method demonstrates how to use the inherited _execute_in_transaction
        method for operations that should return None on error instead of raising.
        """

        async def get_comment_operation(uow: AsyncUnitOfWork) -> CommentOut | None:
            article_repo = ArticleRepository(uow.session)
            comment_repo = CommentRepository(uow.session)
            user_repo = UserRepository(uow.session)

            # Check if article exists
            article = await article_repo.get_by_slug(article_slug)
            if not article or article.id is None:
                return None

            # Get the comment
            comment = await comment_repo.get_by_id(comment_id)
            if not comment or comment.article_id != article.id:
                return None

            # Get author information
            author = await user_repo.get_by_id(comment.author_id)
            if not author:
                return None

            return _build_comment_response(
                comment,
                author_username=author.username,
                author_bio=author.bio or "",
                author_image=author.image or "",
                following=False,
            )

        # Use the inherited _execute_in_transaction with reraise=False
        return await self._execute_in_transaction(
            get_comment_operation, reraise=False, log_errors=True
        )

    async def get_comment_with_manual_transaction(
        self, article_slug: str, comment_id: int
    ) -> CommentOut:
        """
        Example of using the manual transaction context manager.

        This method demonstrates how to use the inherited transaction()
        context manager for manual transaction control.
        """
        async with self.transaction() as uow:
            article_repo = ArticleRepository(uow.session)
            comment_repo = CommentRepository(uow.session)
            user_repo = UserRepository(uow.session)

            # Check if article exists
            article = await article_repo.get_by_slug(article_slug)
            if not article or article.id is None:
                raise ArticleNotFoundError(f"Article with slug '{article_slug}' not found")

            # Get the comment
            comment = await comment_repo.get_by_id(comment_id)
            if not comment:
                raise CommentNotFoundError(f"Comment with ID {comment_id} not found")

            if comment.article_id != article.id:
                raise CommentNotFoundError("Comment does not belong to this article")

            # Get author
            author = await user_repo.get_by_id(comment.author_id)
            if not author:
                raise UserNotFoundError("Comment author not found")

            return _build_comment_response(
                comment,
                author_username=author.username,
                author_bio=author.bio or "",
                author_image=author.image or "",
                following=False,
            )
