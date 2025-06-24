"""
Tests for the feed articles endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_feed_articles_authenticated_user(async_client: AsyncClient) -> None:
    """
    GIVEN: Two users where user1 follows user2, and user2 has created articles
    WHEN: User1 requests their feed
    THEN: User1 should see user2's articles in their feed
    """
    # Create two users
    user1_data = {
        "user": {
            "username": "follower",
            "email": "follower@example.com",
            "password": "password123",
        }
    }
    user2_data = {
        "user": {
            "username": "author",
            "email": "author@example.com",
            "password": "password123",
        }
    }

    # Register both users
    response1 = await async_client.post("/users", json=user1_data)
    assert response1.status_code == 201
    user1_token = response1.json()["user"]["token"]

    response2 = await async_client.post("/users", json=user2_data)
    assert response2.status_code == 201
    user2_token = response2.json()["user"]["token"]

    # User1 follows User2
    headers1 = {"Authorization": f"Token {user1_token}"}
    follow_response = await async_client.post("/profiles/author/follow", headers=headers1)
    assert follow_response.status_code == 200

    # User2 creates an article
    headers2 = {"Authorization": f"Token {user2_token}"}
    article_data = {
        "article": {
            "title": "Test Article",
            "description": "Test description",
            "body": "Test body content",
            "tagList": ["test", "feed"],
        }
    }
    article_response = await async_client.post("/articles", json=article_data, headers=headers2)
    assert article_response.status_code == 201

    # User1 requests their feed
    feed_response = await async_client.get("/articles/feed", headers=headers1)
    assert feed_response.status_code == 200

    feed_data = feed_response.json()
    assert "articles" in feed_data
    assert "articlesCount" in feed_data
    assert feed_data["articlesCount"] == 1
    assert len(feed_data["articles"]) == 1

    article = feed_data["articles"][0]
    assert article["title"] == "Test Article"
    assert article["author"]["username"] == "author"
    assert article["author"]["following"] is True


@pytest.mark.asyncio
async def test_feed_articles_empty_when_not_following_anyone(async_client: AsyncClient) -> None:
    """
    GIVEN: A user who doesn't follow anyone
    WHEN: The user requests their feed
    THEN: The feed should be empty
    """
    user_data = {
        "user": {
            "username": "loner",
            "email": "loner@example.com",
            "password": "password123",
        }
    }

    # Register user
    response = await async_client.post("/users", json=user_data)
    assert response.status_code == 201
    token = response.json()["user"]["token"]

    # Request feed
    headers = {"Authorization": f"Token {token}"}
    feed_response = await async_client.get("/articles/feed", headers=headers)
    assert feed_response.status_code == 200

    feed_data = feed_response.json()
    assert feed_data["articlesCount"] == 0
    assert len(feed_data["articles"]) == 0


@pytest.mark.asyncio
async def test_feed_articles_requires_authentication(async_client: AsyncClient) -> None:
    """
    GIVEN: No authentication token
    WHEN: A request is made to the feed endpoint
    THEN: Should return 401 unauthorized
    """
    response = await async_client.get("/articles/feed")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_feed_articles_pagination(async_client: AsyncClient) -> None:
    """
    GIVEN: A user following another user who has multiple articles
    WHEN: The user requests their feed with pagination parameters
    THEN: Should return paginated results
    """
    # Create two users
    user1_data = {
        "user": {
            "username": "reader",
            "email": "reader@example.com",
            "password": "password123",
        }
    }
    user2_data = {
        "user": {
            "username": "writer",
            "email": "writer@example.com",
            "password": "password123",
        }
    }

    # Register both users
    response1 = await async_client.post("/users", json=user1_data)
    assert response1.status_code == 201
    user1_token = response1.json()["user"]["token"]

    response2 = await async_client.post("/users", json=user2_data)
    assert response2.status_code == 201
    user2_token = response2.json()["user"]["token"]

    # User1 follows User2
    headers1 = {"Authorization": f"Token {user1_token}"}
    follow_response = await async_client.post("/profiles/writer/follow", headers=headers1)
    assert follow_response.status_code == 200

    # User2 creates multiple articles
    headers2 = {"Authorization": f"Token {user2_token}"}
    for i in range(3):
        article_data = {
            "article": {
                "title": f"Article {i + 1}",
                "description": f"Description {i + 1}",
                "body": f"Body content {i + 1}",
                "tagList": ["test"],
            }
        }
        article_response = await async_client.post("/articles", json=article_data, headers=headers2)
        assert article_response.status_code == 201

    # Test pagination - get first 2 articles
    feed_response = await async_client.get("/articles/feed?limit=2&offset=0", headers=headers1)
    assert feed_response.status_code == 200

    feed_data = feed_response.json()
    assert feed_data["articlesCount"] == 3
    assert len(feed_data["articles"]) == 2

    # Test pagination - get next article
    feed_response = await async_client.get("/articles/feed?limit=2&offset=2", headers=headers1)
    assert feed_response.status_code == 200

    feed_data = feed_response.json()
    assert feed_data["articlesCount"] == 3
    assert len(feed_data["articles"]) == 1
