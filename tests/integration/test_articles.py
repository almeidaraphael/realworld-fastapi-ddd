import pytest


@pytest.mark.asyncio
async def test_create_article_success(
    async_client,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN a logged-in user
    WHEN posting a valid article payload to /articles
    THEN the API returns 201 and the created article
    """
    user = user_factory.build()
    username = user.username
    email = user.email

    await register_user_fixture(async_client, username, email, test_password)
    login_resp = await login_user_fixture(async_client, email, test_password)
    token = login_resp.json()["user"]["token"]

    article = article_factory.build(
        title="Test Article",
        description="Test Description",
        body="Test Body",
        tagList=["test", "fastapi"],
    )
    payload = {"article": article.model_dump()}

    resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token}"},
        json=payload,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["article"]["title"] == "Test Article"
    assert data["article"]["description"] == "Test Description"
    assert data["article"]["body"] == "Test Body"
    assert data["article"]["tagList"] == ["test", "fastapi"]
    assert data["article"]["author"]["username"] == username


@pytest.mark.asyncio
async def _setup_articles(
    async_client,
    register_user_fixture,
    login_user_fixture,
    user_factory,
    article_factory,
    test_password,
):
    """Helper to create two users and two articles for list tests."""
    # Create two users with factories
    user1 = user_factory.build()
    user2 = user_factory.build()

    # Register the users
    await register_user_fixture(async_client, user1.username, user1.email, test_password)
    await register_user_fixture(async_client, user2.username, user2.email, test_password)

    # Login the users
    login1 = await login_user_fixture(async_client, user1.email, test_password)
    login2 = await login_user_fixture(async_client, user2.email, test_password)

    # Get tokens
    token1 = login1.json()["user"]["token"]
    token2 = login2.json()["user"]["token"]

    # Create first article with specific tags for testing
    article1 = article_factory.build(tagList=["t1", "t2"], title="A1")
    await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token1}"},
        json={"article": article1.model_dump()},
    )

    # Create second article with specific tags for testing
    article2 = article_factory.build(tagList=["t2", "t3"], title="A2")
    await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token2}"},
        json={"article": article2.model_dump()},
    )

    return user1.username, user2.username


@pytest.mark.asyncio
async def test_list_articles_returns_all(
    async_client,
    register_user_fixture,
    login_user_fixture,
    user_factory,
    article_factory,
    test_password,
):
    """
    GIVEN multiple articles
    WHEN requesting GET /articles
    THEN all articles are returned with correct count
    """
    await _setup_articles(
        async_client,
        register_user_fixture,
        login_user_fixture,
        user_factory,
        article_factory,
        test_password,
    )
    resp = await async_client.get("/api/articles")
    if resp.status_code != 200:
        print(f"Error response: {resp.text}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["articlesCount"] == 2
    assert len(data["articles"]) == 2


@pytest.mark.asyncio
async def test_list_articles_filter_by_tag(
    async_client,
    register_user_fixture,
    login_user_fixture,
    user_factory,
    article_factory,
    test_password,
):
    """
    GIVEN articles with different tags
    WHEN filtering by tag
    THEN only articles with that tag are returned
    """
    await _setup_articles(
        async_client,
        register_user_fixture,
        login_user_fixture,
        user_factory,
        article_factory,
        test_password,
    )
    resp = await async_client.get("/api/articles?tag=t1")
    if resp.status_code != 200:
        print(f"Error response: {resp.text}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["articlesCount"] == 1
    assert data["articles"][0]["title"] == "A1"


@pytest.mark.asyncio
async def test_list_articles_filter_by_author(
    async_client,
    register_user_fixture,
    login_user_fixture,
    user_factory,
    article_factory,
    test_password,
):
    """
    GIVEN articles by different authors
    WHEN filtering by author
    THEN only articles by that author are returned
    """
    username1, username2 = await _setup_articles(
        async_client,
        register_user_fixture,
        login_user_fixture,
        user_factory,
        article_factory,
        test_password,
    )
    resp = await async_client.get(f"/api/articles?author={username2}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["articlesCount"] == 1
    assert data["articles"][0]["title"] == "A2"


@pytest.mark.asyncio
async def test_list_articles_pagination(
    async_client,
    register_user_fixture,
    login_user_fixture,
    user_factory,
    article_factory,
    test_password,
):
    """
    GIVEN multiple articles
    WHEN paginating with limit and offset
    THEN only the correct subset is returned
    """
    await _setup_articles(
        async_client,
        register_user_fixture,
        login_user_fixture,
        user_factory,
        article_factory,
        test_password,
    )
    resp = await async_client.get("/api/articles?limit=1&offset=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["articlesCount"] == 2
    assert len(data["articles"]) == 1


@pytest.mark.asyncio
async def test_list_articles_response_structure(
    async_client,
    register_user_fixture,
    login_user_fixture,
    user_factory,
    article_factory,
    test_password,
):
    """
    GIVEN articles in the system
    WHEN requesting GET /articles
    THEN each article has all required fields in the response
    """
    await _setup_articles(
        async_client,
        register_user_fixture,
        login_user_fixture,
        user_factory,
        article_factory,
        test_password,
    )
    resp = await async_client.get("/api/articles")
    assert resp.status_code == 200
    data = resp.json()
    article = data["articles"][0]
    for field in [
        "slug",
        "title",
        "description",
        "body",
        "tagList",
        "createdAt",
        "updatedAt",
        "favorited",
        "favoritesCount",
        "author",
    ]:
        assert field in article
    for field in ["username", "bio", "image", "following"]:
        assert field in article["author"]


@pytest.mark.asyncio
async def test_get_article_by_slug_success(
    async_client,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN an existing article in the database
    WHEN requesting GET /articles/{slug}
    THEN the API returns 200 and the article details
    """
    user = user_factory.build()
    username = user.username
    email = user.email

    await register_user_fixture(async_client, username, email, test_password)
    login_resp = await login_user_fixture(async_client, email, test_password)
    token = login_resp.json()["user"]["token"]

    # Create an article first
    article = article_factory.build(
        title="Test Article for Get",
        description="Test Description for Get",
        body="Test Body for Get",
        tagList=["test", "get"],
    )
    payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    created_article = create_resp.json()["article"]
    slug = created_article["slug"]

    # Now get the article by slug
    get_resp = await async_client.get(f"/api/articles/{slug}")
    assert get_resp.status_code == 200
    data = get_resp.json()

    assert "article" in data
    article_data = data["article"]
    assert article_data["title"] == "Test Article for Get"
    assert article_data["description"] == "Test Description for Get"
    assert article_data["body"] == "Test Body for Get"
    assert article_data["tagList"] == ["test", "get"]
    assert article_data["author"]["username"] == username
    assert article_data["slug"] == slug
    assert "createdAt" in article_data
    assert "updatedAt" in article_data
    assert "favorited" in article_data
    assert "favoritesCount" in article_data


@pytest.mark.asyncio
async def test_get_article_by_slug_not_found(async_client):
    """
    GIVEN a non-existent article slug
    WHEN requesting GET /articles/{slug}
    THEN the API returns 404
    """
    resp = await async_client.get("/api/articles/non-existent-slug")
    assert resp.status_code == 404
    data = resp.json()
    assert "Article with slug 'non-existent-slug' not found" in data["detail"]


@pytest.mark.asyncio
async def test_get_article_by_slug_with_authenticated_user(
    async_client,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN an authenticated user and an existing article
    WHEN requesting GET /articles/{slug} with authentication
    THEN the API returns 200 with personalized data (favorited, following status)
    """
    # Create author user
    author = user_factory.build()
    author_username = author.username
    author_email = author.email

    await register_user_fixture(async_client, author_username, author_email, test_password)
    author_login_resp = await login_user_fixture(async_client, author_email, test_password)
    author_token = author_login_resp.json()["user"]["token"]

    # Create another user (reader)
    reader = user_factory.build()
    reader_username = reader.username
    reader_email = reader.email

    await register_user_fixture(async_client, reader_username, reader_email, test_password)
    reader_login_resp = await login_user_fixture(async_client, reader_email, test_password)
    reader_token = reader_login_resp.json()["user"]["token"]

    # Create an article as author
    article = article_factory.build(
        title="Test Article with Auth",
        description="Test Description with Auth",
        body="Test Body with Auth",
        tagList=["auth", "test"],
    )
    payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {author_token}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    created_article = create_resp.json()["article"]
    slug = created_article["slug"]

    # Get the article as the reader (authenticated)
    get_resp = await async_client.get(
        f"/api/articles/{slug}", headers={"Authorization": f"Token {reader_token}"}
    )
    assert get_resp.status_code == 200
    data = get_resp.json()

    assert "article" in data
    article_data = data["article"]
    assert article_data["title"] == "Test Article with Auth"
    assert article_data["author"]["username"] == author_username
    # Since reader is not following author and hasn't favorited, these should be False
    assert article_data["favorited"] is False
    assert article_data["author"]["following"] is False


@pytest.mark.asyncio
async def test_update_article_success(
    async_client,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN a logged-in user who created an article
    WHEN updating the article with valid data
    THEN the API returns 200 and the updated article with new slug if title changed
    """
    user = user_factory.build()
    username = user.username
    email = user.email

    await register_user_fixture(async_client, username, email, test_password)
    login_resp = await login_user_fixture(async_client, email, test_password)
    token = login_resp.json()["user"]["token"]

    # Create an article
    article = article_factory.build(
        title="Original Title",
        description="Original Description",
        body="Original Body",
        tagList=["test"],
    )
    payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    created_article = create_resp.json()["article"]
    original_slug = created_article["slug"]

    # Update the article
    update_payload = {
        "article": {
            "title": "Updated Title",
            "description": "Updated Description",
            "body": "Updated Body",
        }
    }

    update_resp = await async_client.put(
        f"/api/articles/{original_slug}",
        headers={"Authorization": f"Token {token}"},
        json=update_payload,
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()

    assert "article" in updated_data
    updated_article = updated_data["article"]
    assert updated_article["title"] == "Updated Title"
    assert updated_article["description"] == "Updated Description"
    assert updated_article["body"] == "Updated Body"
    assert updated_article["author"]["username"] == username
    # Slug should change when title changes
    assert updated_article["slug"] != original_slug
    assert "updated-title" in updated_article["slug"]


@pytest.mark.asyncio
async def test_update_article_not_found(
    async_client,
    user_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN a logged-in user
    WHEN trying to update a non-existent article
    THEN the API returns 404
    """
    user = user_factory.build()
    username = user.username
    email = user.email

    await register_user_fixture(async_client, username, email, test_password)
    login_resp = await login_user_fixture(async_client, email, test_password)
    token = login_resp.json()["user"]["token"]

    payload = {"article": {"title": "Updated Title"}}

    resp = await async_client.put(
        "/api/articles/non-existent-slug",
        headers={"Authorization": f"Token {token}"},
        json=payload,
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_article_unauthorized(
    async_client,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN two users, where one creates an article
    WHEN the other user tries to update the article
    THEN the API returns 403
    """
    # Create first user and article
    user1 = user_factory.build()
    await register_user_fixture(async_client, user1.username, user1.email, test_password)
    login_resp1 = await login_user_fixture(async_client, user1.email, test_password)
    token1 = login_resp1.json()["user"]["token"]

    article = article_factory.build(title="Original Title")
    payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token1}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    slug = create_resp.json()["article"]["slug"]

    # Create second user
    user2 = user_factory.build()
    await register_user_fixture(async_client, user2.username, user2.email, test_password)
    login_resp2 = await login_user_fixture(async_client, user2.email, test_password)
    token2 = login_resp2.json()["user"]["token"]

    # Try to update with second user
    update_payload = {"article": {"title": "Unauthorized Update"}}

    resp = await async_client.put(
        f"/api/articles/{slug}",
        headers={"Authorization": f"Token {token2}"},
        json=update_payload,
    )
    assert resp.status_code == 403
    assert "not authorized" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_article_partial_update(
    async_client,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN a logged-in user with an existing article
    WHEN updating only one field (partial update)
    THEN the API returns 200 and only that field is updated
    """
    user = user_factory.build()
    username = user.username
    email = user.email

    await register_user_fixture(async_client, username, email, test_password)
    login_resp = await login_user_fixture(async_client, email, test_password)
    token = login_resp.json()["user"]["token"]

    # Create article
    article = article_factory.build(
        title="Original Title", description="Original Description", body="Original Body"
    )
    payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    slug = create_resp.json()["article"]["slug"]
    original_created_at = create_resp.json()["article"]["createdAt"]

    # Update only the description
    update_payload = {"article": {"description": "Updated Description Only"}}

    update_resp = await async_client.put(
        f"/api/articles/{slug}",
        headers={"Authorization": f"Token {token}"},
        json=update_payload,
    )
    assert update_resp.status_code == 200

    updated_data = update_resp.json()
    assert updated_data["article"]["title"] == "Original Title"  # unchanged
    assert updated_data["article"]["description"] == "Updated Description Only"  # changed
    assert updated_data["article"]["body"] == "Original Body"  # unchanged
    assert updated_data["article"]["author"]["username"] == username
    assert updated_data["article"]["createdAt"] == original_created_at  # unchanged
    # updatedAt should be different
    assert updated_data["article"]["updatedAt"] != original_created_at


@pytest.mark.asyncio
async def test_update_article_title_changes_slug(
    async_client,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN a logged-in user with an existing article
    WHEN updating the title
    THEN the API returns 200 and the slug is updated to match the new title
    """
    user = user_factory.build()
    username = user.username
    email = user.email

    await register_user_fixture(async_client, username, email, test_password)
    login_resp = await login_user_fixture(async_client, email, test_password)
    token = login_resp.json()["user"]["token"]

    # Create article
    article = article_factory.build(title="Original Title")
    payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    original_slug = create_resp.json()["article"]["slug"]

    # Update the title
    new_title = "Completely New Title"
    update_payload = {"article": {"title": new_title}}

    update_resp = await async_client.put(
        f"/api/articles/{original_slug}",
        headers={"Authorization": f"Token {token}"},
        json=update_payload,
    )
    assert update_resp.status_code == 200

    updated_data = update_resp.json()
    assert updated_data["article"]["title"] == new_title
    new_slug = updated_data["article"]["slug"]
    assert new_slug != original_slug
    assert "completely-new-title" in new_slug  # slug should be based on new title

    # Verify the article can be fetched with the new slug
    get_resp = await async_client.get(f"/api/articles/{new_slug}")
    assert get_resp.status_code == 200
    assert get_resp.json()["article"]["title"] == new_title

    # Verify the old slug no longer works
    old_get_resp = await async_client.get(f"/api/articles/{original_slug}")
    assert old_get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_article_success(
    async_client,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN a logged-in user who created an article
    WHEN deleting the article by slug
    THEN the API returns 200 and the article is removed from the database
    """
    user = user_factory.build()
    username = user.username
    email = user.email

    await register_user_fixture(async_client, username, email, test_password)
    login_resp = await login_user_fixture(async_client, email, test_password)
    token = login_resp.json()["user"]["token"]

    # Create an article
    article = article_factory.build(
        title="Article to Delete",
        description="This article will be deleted",
        body="Test Body",
        tagList=["test", "delete"],
    )
    payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    created_article = create_resp.json()["article"]
    slug = created_article["slug"]

    # Verify the article exists
    get_resp = await async_client.get(f"/api/articles/{slug}")
    assert get_resp.status_code == 200

    # Delete the article
    delete_resp = await async_client.delete(
        f"/api/articles/{slug}",
        headers={"Authorization": f"Token {token}"},
    )
    assert delete_resp.status_code == 200

    # Verify the article no longer exists
    get_after_delete_resp = await async_client.get(f"/api/articles/{slug}")
    assert get_after_delete_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_article_not_found(
    async_client,
    user_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN a logged-in user
    WHEN trying to delete a non-existent article
    THEN the API returns 404
    """
    user = user_factory.build()
    username = user.username
    email = user.email

    await register_user_fixture(async_client, username, email, test_password)
    login_resp = await login_user_fixture(async_client, email, test_password)
    token = login_resp.json()["user"]["token"]

    # Try to delete non-existent article
    resp = await async_client.delete(
        "/api/articles/non-existent-slug",
        headers={"Authorization": f"Token {token}"},
    )
    assert resp.status_code == 404
    assert "Article with slug 'non-existent-slug' not found" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_delete_article_unauthorized(
    async_client,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN two users, where one creates an article
    WHEN the other user tries to delete the article
    THEN the API returns 403
    """
    # Create first user and article
    user1 = user_factory.build()
    await register_user_fixture(async_client, user1.username, user1.email, test_password)
    login_resp1 = await login_user_fixture(async_client, user1.email, test_password)
    token1 = login_resp1.json()["user"]["token"]

    article = article_factory.build(title="Article by User 1")
    payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token1}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    slug = create_resp.json()["article"]["slug"]

    # Create second user
    user2 = user_factory.build()
    await register_user_fixture(async_client, user2.username, user2.email, test_password)
    login_resp2 = await login_user_fixture(async_client, user2.email, test_password)
    token2 = login_resp2.json()["user"]["token"]

    # Try to delete with second user
    resp = await async_client.delete(
        f"/api/articles/{slug}",
        headers={"Authorization": f"Token {token2}"},
    )
    assert resp.status_code == 403
    assert "Only the author can delete this article" in resp.json()["detail"]

    # Verify the article still exists
    get_resp = await async_client.get(f"/api/articles/{slug}")
    assert get_resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_article_requires_authentication(
    async_client,
    user_factory,
    article_factory,
    register_user_fixture,
    login_user_fixture,
    test_password,
):
    """
    GIVEN an existing article
    WHEN trying to delete without authentication
    THEN the API returns 401
    """
    # Create user and article
    user = user_factory.build()
    await register_user_fixture(async_client, user.username, user.email, test_password)
    login_resp = await login_user_fixture(async_client, user.email, test_password)
    token = login_resp.json()["user"]["token"]

    article = article_factory.build(title="Article to Delete Without Auth")
    payload = {"article": article.model_dump()}

    create_resp = await async_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {token}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    slug = create_resp.json()["article"]["slug"]

    # Try to delete without authentication
    resp = await async_client.delete(f"/api/articles/{slug}")
    assert resp.status_code == 401

    # Verify the article still exists
    get_resp = await async_client.get(f"/api/articles/{slug}")
    assert get_resp.status_code == 200
