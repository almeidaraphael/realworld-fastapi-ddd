"""
Integration tests for comment endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_comment_success(
    async_client: AsyncClient,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN an authenticated user and an existing article
    WHEN posting a valid comment to /articles/{slug}/comments
    THEN the API returns 201 and the created comment
    """
    # Create user and login
    user = user_factory.build()
    await register_user_fixture(async_client, user.username, user.email, test_password)
    login_resp = await login_user_fixture(async_client, user.email, test_password)
    token = login_resp.json()["user"]["token"]

    # Create article
    article = article_factory.build(
        title="Test Article for Comments",
        description="Article for testing comments",
        body="Test content",
        tagList=["test"],
    )
    article_payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token}"},
        json=article_payload,
    )
    assert create_resp.status_code == 201
    slug = create_resp.json()["article"]["slug"]

    # Create comment
    comment_payload = {"comment": {"body": "This is a test comment on the article"}}

    comment_resp = await async_client.post(
        f"/api/articles/{slug}/comments",
        headers={"Authorization": f"Token {token}"},
        json=comment_payload,
    )

    assert comment_resp.status_code == 201
    data = comment_resp.json()
    assert "comment" in data
    comment_data = data["comment"]
    assert comment_data["body"] == "This is a test comment on the article"
    assert comment_data["author"]["username"] == user.username
    assert "id" in comment_data
    assert "createdAt" in comment_data
    assert "updatedAt" in comment_data


@pytest.mark.asyncio
async def test_create_comment_unauthorized(async_client: AsyncClient):
    """
    GIVEN no authentication
    WHEN posting a comment to /articles/{slug}/comments
    THEN the API returns 401
    """
    comment_payload = {"comment": {"body": "This should fail"}}

    resp = await async_client.post(
        "/api/articles/test-slug/comments",
        json=comment_payload,
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_comment_article_not_found(
    async_client: AsyncClient,
    user_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN an authenticated user
    WHEN posting a comment to a non-existent article
    THEN the API returns 404
    """
    # Create user and login
    user = user_factory.build()
    await register_user_fixture(async_client, user.username, user.email, test_password)
    login_resp = await login_user_fixture(async_client, user.email, test_password)
    token = login_resp.json()["user"]["token"]

    comment_payload = {"comment": {"body": "Comment on non-existent article"}}

    resp = await async_client.post(
        "/api/articles/non-existent-slug/comments",
        headers={"Authorization": f"Token {token}"},
        json=comment_payload,
    )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_comments_success(
    async_client: AsyncClient,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN an article with comments
    WHEN requesting GET /articles/{slug}/comments
    THEN the API returns 200 and all comments
    """
    # Create two users
    user1 = user_factory.build()
    user2 = user_factory.build()

    await register_user_fixture(async_client, user1.username, user1.email, test_password)
    login_resp1 = await login_user_fixture(async_client, user1.email, test_password)
    token1 = login_resp1.json()["user"]["token"]

    await register_user_fixture(async_client, user2.username, user2.email, test_password)
    login_resp2 = await login_user_fixture(async_client, user2.email, test_password)
    token2 = login_resp2.json()["user"]["token"]

    # User1 creates article
    article = article_factory.build(
        title="Article with Comments",
        description="Testing comments",
        body="Test content",
        tagList=["test"],
    )
    article_payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token1}"},
        json=article_payload,
    )
    assert create_resp.status_code == 201
    slug = create_resp.json()["article"]["slug"]

    # Both users add comments
    comment1_payload = {"comment": {"body": "First comment by user1"}}
    comment2_payload = {"comment": {"body": "Second comment by user2"}}

    await async_client.post(
        f"/api/articles/{slug}/comments",
        headers={"Authorization": f"Token {token1}"},
        json=comment1_payload,
    )

    await async_client.post(
        f"/api/articles/{slug}/comments",
        headers={"Authorization": f"Token {token2}"},
        json=comment2_payload,
    )

    # Get comments
    get_resp = await async_client.get(f"/api/articles/{slug}/comments")
    assert get_resp.status_code == 200

    data = get_resp.json()
    assert "comments" in data
    comments = data["comments"]
    assert len(comments) == 2

    # Comments should be ordered by creation time (newest first)
    assert comments[0]["body"] == "Second comment by user2"
    assert comments[0]["author"]["username"] == user2.username
    assert comments[1]["body"] == "First comment by user1"
    assert comments[1]["author"]["username"] == user1.username


@pytest.mark.asyncio
async def test_get_comments_article_not_found(async_client: AsyncClient):
    """
    GIVEN a non-existent article
    WHEN requesting GET /articles/{slug}/comments
    THEN the API returns 404
    """
    resp = await async_client.get("/api/articles/non-existent-slug/comments")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_comment_success(
    async_client: AsyncClient,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN a user who created a comment
    WHEN deleting the comment via DELETE /articles/{slug}/comments/{id}
    THEN the API returns 204 and the comment is removed
    """
    # Create user and login
    user = user_factory.build()
    await register_user_fixture(async_client, user.username, user.email, test_password)
    login_resp = await login_user_fixture(async_client, user.email, test_password)
    token = login_resp.json()["user"]["token"]

    # Create article
    article = article_factory.build(
        title="Article for Comment Deletion",
        description="Testing comment deletion",
        body="Test content",
        tagList=["test"],
    )
    article_payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token}"},
        json=article_payload,
    )
    assert create_resp.status_code == 201
    slug = create_resp.json()["article"]["slug"]

    # Create comment
    comment_payload = {"comment": {"body": "Comment to be deleted"}}

    comment_resp = await async_client.post(
        f"/api/articles/{slug}/comments",
        headers={"Authorization": f"Token {token}"},
        json=comment_payload,
    )
    assert comment_resp.status_code == 201
    comment_id = comment_resp.json()["comment"]["id"]

    # Delete comment
    delete_resp = await async_client.delete(
        f"/api/articles/{slug}/comments/{comment_id}",
        headers={"Authorization": f"Token {token}"},
    )
    assert delete_resp.status_code == 204

    # Verify comment is deleted - get comments should return empty list
    get_resp = await async_client.get(f"/api/articles/{slug}/comments")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert len(data["comments"]) == 0


@pytest.mark.asyncio
async def test_delete_comment_unauthorized(
    async_client: AsyncClient,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN a comment created by another user
    WHEN trying to delete it
    THEN the API returns 403
    """
    # Create two users
    user1 = user_factory.build()
    user2 = user_factory.build()

    await register_user_fixture(async_client, user1.username, user1.email, test_password)
    login_resp1 = await login_user_fixture(async_client, user1.email, test_password)
    token1 = login_resp1.json()["user"]["token"]

    await register_user_fixture(async_client, user2.username, user2.email, test_password)
    login_resp2 = await login_user_fixture(async_client, user2.email, test_password)
    token2 = login_resp2.json()["user"]["token"]

    # User1 creates article and comment
    article = article_factory.build(
        title="Article for Unauthorized Delete",
        description="Testing unauthorized comment deletion",
        body="Test content",
        tagList=["test"],
    )
    article_payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token1}"},
        json=article_payload,
    )
    assert create_resp.status_code == 201
    slug = create_resp.json()["article"]["slug"]

    comment_payload = {"comment": {"body": "Comment by user1"}}

    comment_resp = await async_client.post(
        f"/api/articles/{slug}/comments",
        headers={"Authorization": f"Token {token1}"},
        json=comment_payload,
    )
    assert comment_resp.status_code == 201
    comment_id = comment_resp.json()["comment"]["id"]

    # User2 tries to delete user1's comment
    delete_resp = await async_client.delete(
        f"/api/articles/{slug}/comments/{comment_id}",
        headers={"Authorization": f"Token {token2}"},
    )
    assert delete_resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_comment_not_found(
    async_client: AsyncClient,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN an authenticated user and an existing article
    WHEN trying to delete a non-existent comment
    THEN the API returns 404
    """
    # Create user and login
    user = user_factory.build()
    await register_user_fixture(async_client, user.username, user.email, test_password)
    login_resp = await login_user_fixture(async_client, user.email, test_password)
    token = login_resp.json()["user"]["token"]

    # Create article
    article = article_factory.build(
        title="Article for Non-existent Comment",
        description="Testing non-existent comment deletion",
        body="Test content",
        tagList=["test"],
    )
    article_payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token}"},
        json=article_payload,
    )
    assert create_resp.status_code == 201
    slug = create_resp.json()["article"]["slug"]

    # Try to delete non-existent comment
    delete_resp = await async_client.delete(
        f"/api/articles/{slug}/comments/999999",
        headers={"Authorization": f"Token {token}"},
    )
    assert delete_resp.status_code == 404
