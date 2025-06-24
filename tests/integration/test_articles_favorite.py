"""Test for article favorite/unfavorite functionality."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_favorite_unfavorite_article_workflow(
    async_client: AsyncClient,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
) -> None:
    """
    GIVEN a user and an article
    WHEN the user favorites and then unfavorites the article
    THEN the article's favorited status and count should update correctly
    """
    # Create and register user
    user = user_factory.build()
    username = user.username
    email = user.email

    await register_user_fixture(async_client, username, email, test_password)
    login_resp = await login_user_fixture(async_client, email, test_password)
    token = login_resp.json()["user"]["token"]
    headers = {"Authorization": f"Token {token}"}

    # Create an article
    article = article_factory.build(
        title="Test Favorite Article",
        description="A test article for favorites",
        body="This is a test article body for favorites",
        tagList=["test", "favorite"],
    )
    payload = {"article": article.model_dump()}

    response = await async_client.post("/api/articles", json=payload, headers=headers)
    assert response.status_code == 201
    created_article = response.json()["article"]
    slug = created_article["slug"]

    # Initially not favorited
    assert created_article["favorited"] is False
    assert created_article["favoritesCount"] == 0

    # Favorite the article
    response = await async_client.post(f"/api/articles/{slug}/favorite", headers=headers)
    assert response.status_code == 200
    favorited_article = response.json()["article"]
    assert favorited_article["favorited"] is True
    assert favorited_article["favoritesCount"] == 1

    # Unfavorite the article
    response = await async_client.delete(f"/api/articles/{slug}/favorite", headers=headers)
    assert response.status_code == 200
    unfavorited_article = response.json()["article"]
    assert unfavorited_article["favorited"] is False
    assert unfavorited_article["favoritesCount"] == 0


@pytest.mark.asyncio
async def test_favorite_nonexistent_article(
    async_client: AsyncClient,
    user_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
) -> None:
    """
    GIVEN a user
    WHEN they try to favorite a non-existent article
    THEN they should get a 404 error
    """
    # Create and register user
    user = user_factory.build()
    username = user.username
    email = user.email

    await register_user_fixture(async_client, username, email, test_password)
    login_resp = await login_user_fixture(async_client, email, test_password)
    token = login_resp.json()["user"]["token"]
    headers = {"Authorization": f"Token {token}"}

    # Try to favorite non-existent article
    response = await async_client.post("/api/articles/nonexistent-slug/favorite", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_favorite_without_authentication(async_client: AsyncClient) -> None:
    """
    GIVEN no authentication
    WHEN trying to favorite an article
    THEN should get a 401 error
    """
    response = await async_client.post("/api/articles/some-slug/favorite")
    assert response.status_code == 401
