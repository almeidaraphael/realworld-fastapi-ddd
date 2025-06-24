"""Integration tests for tags endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_tags_empty(async_client: AsyncClient) -> None:
    """
    GIVEN an empty database
    WHEN the GET /api/tags endpoint is called
    THEN it should return status 200 and an empty tags array
    """
    response = await async_client.get("/api/tags")
    assert response.status_code == 200
    data = response.json()
    assert "tags" in data
    assert isinstance(data["tags"], list)


@pytest.mark.asyncio
async def test_get_tags_with_articles(async_client: AsyncClient, user_factory) -> None:
    """
    GIVEN articles with tags exist in the database
    WHEN the GET /api/tags endpoint is called
    THEN it should return status 200 and a list of unique tags
    """
    # Create a user first
    user = user_factory.build()
    user_data = {
        "user": {"username": user.username, "email": user.email, "password": "testpass123"}
    }
    user_response = await async_client.post("/api/users", json=user_data)
    assert user_response.status_code == 201
    token = user_response.json()["user"]["token"]
    headers = {"Authorization": f"Token {token}"}

    # Create articles with tags
    article1_data = {
        "article": {
            "title": "Test Article 1",
            "description": "A test article",
            "body": "This is a test article body",
            "tagList": ["python", "fastapi", "testing"],
        }
    }
    article2_data = {
        "article": {
            "title": "Test Article 2",
            "description": "Another test article",
            "body": "This is another test article body",
            "tagList": ["python", "backend", "api"],
        }
    }

    # Create the articles
    article1_response = await async_client.post(
        "/api/articles", json=article1_data, headers=headers
    )
    assert article1_response.status_code == 201

    article2_response = await async_client.post(
        "/api/articles", json=article2_data, headers=headers
    )
    assert article2_response.status_code == 201

    # Get tags
    response = await async_client.get("/api/tags")
    assert response.status_code == 200
    data = response.json()

    assert "tags" in data
    tags = data["tags"]
    assert isinstance(tags, list)

    # Should contain all unique tags sorted alphabetically
    expected_tags = ["api", "backend", "fastapi", "python", "testing"]
    assert tags == expected_tags
