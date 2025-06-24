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
        "/articles",
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
        "/articles",
        headers={"Authorization": f"Token {token1}"},
        json={"article": article1.model_dump()},
    )

    # Create second article with specific tags for testing
    article2 = article_factory.build(tagList=["t2", "t3"], title="A2")
    await async_client.post(
        "/articles",
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
    resp = await async_client.get("/articles")
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
    resp = await async_client.get("/articles?tag=t1")
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
    resp = await async_client.get(f"/articles?author={username2}")
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
    resp = await async_client.get("/articles?limit=1&offset=1")
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
    resp = await async_client.get("/articles")
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
        "/articles",
        headers={"Authorization": f"Token {token}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    created_article = create_resp.json()["article"]
    slug = created_article["slug"]

    # Now get the article by slug
    get_resp = await async_client.get(f"/articles/{slug}")
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
    resp = await async_client.get("/articles/non-existent-slug")
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
        "/articles",
        headers={"Authorization": f"Token {author_token}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    created_article = create_resp.json()["article"]
    slug = created_article["slug"]

    # Get the article as the reader (authenticated)
    get_resp = await async_client.get(
        f"/articles/{slug}", headers={"Authorization": f"Token {reader_token}"}
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
