"""
Unit tests for comment service.
"""

import pytest

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.domain.articles.exceptions import ArticleNotFoundError
from app.domain.comments.exceptions import CommentPermissionError
from app.domain.comments.models import Comment
from app.domain.comments.schemas import CommentCreate
from app.service_layer.comments.services import CommentService


@pytest.fixture
def mock_uow(mocker):
    """Create a mock unit of work."""
    uow = mocker.Mock(spec=AsyncUnitOfWork)
    uow.session = mocker.Mock()
    uow.__aenter__ = mocker.AsyncMock(return_value=uow)
    uow.__aexit__ = mocker.AsyncMock(return_value=None)
    return uow


@pytest.fixture
def comment_service(mock_uow):
    """Create a comment service with mocked dependencies."""
    return CommentService()


@pytest.fixture
def sample_comment_data():
    """Sample comment creation data."""
    return CommentCreate(body="This is a test comment")


@pytest.fixture
def sample_article(mocker):
    """Sample article for testing."""
    article = mocker.Mock()
    article.id = 1
    article.slug = "test-article"
    return article


@pytest.fixture
def sample_user(mocker):
    """Sample user for testing."""
    user = mocker.Mock()
    user.id = 1
    user.username = "testuser"
    user.bio = "Test bio"
    user.image = "test.jpg"
    return user


@pytest.fixture
def sample_comment():
    """Sample comment for testing."""
    return Comment(
        id=1,
        body="Test comment",
        article_id=1,
        author_id=1,
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00",
    )


@pytest.mark.asyncio
async def test_add_comment_to_article_success(
    comment_service, mock_uow, sample_comment_data, sample_article, sample_user, mocker
):
    """
    GIVEN a valid article slug, comment data, and authenticated user
    WHEN adding a comment to the article
    THEN the comment should be created and returned successfully
    """
    # Mock the transactional decorator to pass through the mocked UoW
    mocker.patch("app.shared.transaction.AsyncUnitOfWork", return_value=mock_uow)

    # Mock repositories
    article_repo_mock = mocker.Mock()
    comment_repo_mock = mocker.Mock()
    user_repo_mock = mocker.Mock()

    # Mock repository classes
    mocker.patch(
        "app.service_layer.comments.services.ArticleRepository", return_value=article_repo_mock
    )
    mocker.patch(
        "app.service_layer.comments.services.CommentRepository", return_value=comment_repo_mock
    )
    mocker.patch("app.service_layer.comments.services.UserRepository", return_value=user_repo_mock)

    # Set up return values
    article_repo_mock.get_by_slug = mocker.AsyncMock(return_value=sample_article)
    user_repo_mock.get_by_id = mocker.AsyncMock(return_value=sample_user)

    created_comment = Comment(
        id=1,
        body=sample_comment_data.body,
        article_id=sample_article.id,
        author_id=sample_user.id,
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00",
    )
    comment_repo_mock.add = mocker.AsyncMock(return_value=created_comment)

    # Execute
    result = await comment_service.add_comment_to_article(
        article_slug="test-article", comment_data=sample_comment_data, current_user_id=1
    )

    # Verify
    assert result.body == sample_comment_data.body
    assert result.author.username == sample_user.username
    assert result.id == 1
    article_repo_mock.get_by_slug.assert_called_once_with("test-article")
    user_repo_mock.get_by_id.assert_called_once_with(1)
    comment_repo_mock.add.assert_called_once()


@pytest.mark.asyncio
async def test_add_comment_article_not_found(
    comment_service, mock_uow, sample_comment_data, mocker
):
    """
    GIVEN an invalid article slug
    WHEN adding a comment to the article
    THEN an ArticleNotFoundError should be raised
    """
    # Mock the transactional decorator to pass through the mocked UoW
    mocker.patch("app.shared.transaction.AsyncUnitOfWork", return_value=mock_uow)

    # Mock repositories
    article_repo_mock = mocker.Mock()
    mocker.patch(
        "app.service_layer.comments.services.ArticleRepository", return_value=article_repo_mock
    )

    # Set up return values
    article_repo_mock.get_by_slug = mocker.AsyncMock(return_value=None)

    # Execute and verify
    with pytest.raises(ArticleNotFoundError, match="Article with slug 'nonexistent' not found"):
        await comment_service.add_comment_to_article(
            article_slug="nonexistent", comment_data=sample_comment_data, current_user_id=1
        )


@pytest.mark.asyncio
async def test_delete_comment_success(
    comment_service, mock_uow, sample_article, sample_comment, mocker
):
    """
    GIVEN a valid article slug, comment ID, and comment author
    WHEN deleting the comment
    THEN the comment should be deleted successfully
    """
    # Mock the transactional decorator to pass through the mocked UoW
    mocker.patch("app.shared.transaction.AsyncUnitOfWork", return_value=mock_uow)

    # Mock repositories
    article_repo_mock = mocker.Mock()
    comment_repo_mock = mocker.Mock()

    mocker.patch(
        "app.service_layer.comments.services.ArticleRepository", return_value=article_repo_mock
    )
    mocker.patch(
        "app.service_layer.comments.services.CommentRepository", return_value=comment_repo_mock
    )

    # Set up return values
    article_repo_mock.get_by_slug = mocker.AsyncMock(return_value=sample_article)
    comment_repo_mock.get_by_id = mocker.AsyncMock(return_value=sample_comment)
    comment_repo_mock.delete = mocker.AsyncMock()

    # Execute
    await comment_service.delete_comment(
        article_slug="test-article",
        comment_id=1,
        current_user_id=1,  # Same as comment author
    )

    # Verify
    article_repo_mock.get_by_slug.assert_called_once_with("test-article")
    comment_repo_mock.get_by_id.assert_called_once_with(1)
    comment_repo_mock.delete.assert_called_once_with(sample_comment)


@pytest.mark.asyncio
async def test_delete_comment_permission_denied(
    comment_service, mock_uow, sample_article, sample_comment, mocker
):
    """
    GIVEN a valid comment but different user
    WHEN trying to delete the comment
    THEN a CommentPermissionError should be raised
    """
    # Mock the transactional decorator to pass through the mocked UoW
    mocker.patch("app.shared.transaction.AsyncUnitOfWork", return_value=mock_uow)

    # Mock repositories
    article_repo_mock = mocker.Mock()
    comment_repo_mock = mocker.Mock()

    mocker.patch(
        "app.service_layer.comments.services.ArticleRepository", return_value=article_repo_mock
    )
    mocker.patch(
        "app.service_layer.comments.services.CommentRepository", return_value=comment_repo_mock
    )

    # Set up return values
    article_repo_mock.get_by_slug = mocker.AsyncMock(return_value=sample_article)
    comment_repo_mock.get_by_id = mocker.AsyncMock(return_value=sample_comment)

    # Execute and verify
    with pytest.raises(CommentPermissionError, match="You can only delete your own comments"):
        await comment_service.delete_comment(
            article_slug="test-article",
            comment_id=1,
            current_user_id=2,  # Different from comment author (1)
        )
