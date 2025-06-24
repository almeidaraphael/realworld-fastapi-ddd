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
