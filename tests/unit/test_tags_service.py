"""Unit tests for tags service layer."""

from unittest.mock import AsyncMock

import pytest

from app.service_layer.tags.services import get_tags


@pytest.mark.asyncio
async def test_get_tags_service(mocker) -> None:
    """
    GIVEN a mocked tags repository
    WHEN get_tags service is called
    THEN it should return the tags from the repository
    """
    # Mock the repository
    mock_tags_repo = AsyncMock()
    mock_tags_repo.get_all_tags.return_value = ["python", "fastapi", "testing"]

    # Mock the TagsRepository class
    mocker.patch("app.service_layer.tags.services.TagsRepository", return_value=mock_tags_repo)

    # Mock the AsyncUnitOfWork
    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    mocker.patch("app.service_layer.tags.services.AsyncUnitOfWork", return_value=mock_uow)

    # Call the service
    result = await get_tags()

    # Verify
    assert result == ["python", "fastapi", "testing"]
    mock_tags_repo.get_all_tags.assert_called_once()
