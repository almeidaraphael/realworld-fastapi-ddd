import pytest


@pytest.mark.asyncio
async def test_create_article_success(
    async_client, user_factory, register_user_fixture, login_user_fixture
):
    """
    GIVEN a logged-in user
    WHEN posting a valid article payload to /articles
    THEN the API returns 201 and the created article
    """
    await register_user_fixture(async_client, "author1", "author1@example.com", "password123")
    login_resp = await login_user_fixture(async_client, "author1@example.com", "password123")
    token = login_resp.json()["user"]["token"]
    payload = {
        "title": "Test Article",
        "description": "Test Description",
        "body": "Test Body",
        "tagList": ["test", "fastapi"],
    }
    resp = await async_client.post(
        "/articles",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["article"]["title"] == "Test Article"
    assert data["article"]["description"] == "Test Description"
    assert data["article"]["body"] == "Test Body"
    assert data["article"]["tagList"] == ["test", "fastapi"]
    assert data["article"]["author"]["username"] == "author1"
