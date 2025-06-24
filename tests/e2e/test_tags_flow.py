"""End-to-end tests for tags functionality."""

import pytest
from httpx import AsyncClient

from tests.helpers import register_user


@pytest.mark.asyncio
async def test_tags_e2e_flow(async_client: AsyncClient, user_factory) -> None:
    """
    GIVEN a complete tags workflow
    WHEN creating articles with tags and retrieving tags
    THEN all tags should be available through the tags endpoint
    """
    # Create a user for authentication
    user = user_factory.build()
    resp = await register_user(async_client, user.username, user.email, "password123")
    assert resp.status_code == 201

    token = resp.json()["user"]["token"]
    headers = {"Authorization": f"Token {token}"}

    # Initially, get all tags (should include existing ones)
    tags_response = await async_client.get("/api/tags")
    assert tags_response.status_code == 200
    initial_tags = set(tags_response.json()["tags"])

    # Create first article with specific tags
    article1_data = {
        "article": {
            "title": "E2E Test Article 1",
            "description": "First test article",
            "body": "Content of the first test article",
            "tagList": ["e2e", "integration", "fastapi"],
        }
    }

    article1_response = await async_client.post(
        "/api/articles", json=article1_data, headers=headers
    )
    assert article1_response.status_code == 201

    # Create second article with overlapping and new tags
    article2_data = {
        "article": {
            "title": "E2E Test Article 2",
            "description": "Second test article",
            "body": "Content of the second test article",
            "tagList": ["e2e", "testing", "python", "backend"],
        }
    }

    article2_response = await async_client.post(
        "/api/articles", json=article2_data, headers=headers
    )
    assert article2_response.status_code == 201

    # Get tags again and verify all new tags are present
    final_tags_response = await async_client.get("/api/tags")
    assert final_tags_response.status_code == 200

    all_tags = set(final_tags_response.json()["tags"])
    new_tags = {"e2e", "integration", "fastapi", "testing", "python", "backend"}

    # Verify all new tags are present
    assert new_tags.issubset(all_tags)

    # Verify tags are sorted
    tags_list = final_tags_response.json()["tags"]
    assert tags_list == sorted(tags_list)

    # Verify we have more tags than initially
    assert len(all_tags) >= len(initial_tags) + len(new_tags)
