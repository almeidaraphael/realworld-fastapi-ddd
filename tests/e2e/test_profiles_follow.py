import pytest
from httpx import AsyncClient

from tests.helpers import login_user, register_user


@pytest.mark.asyncio
async def test_follow_profile_success(async_client: AsyncClient, user_read_factory) -> None:
    """
    GIVEN two registered users
    WHEN one user follows the other
    THEN the API returns 200 and the profile shows following=True
    """
    user1 = user_read_factory.build(username="user1_test", email="user1_test@example.com")
    user2 = user_read_factory.build(username="user2_test", email="user2_test@example.com")
    user1_data = user1.model_dump()
    user2_data = user2.model_dump()
    user1_username = user1_data["username"]
    user1_email = user1_data["email"]
    user2_username = user2_data["username"]
    user2_email = user2_data["email"]
    assert user1_username != user2_username, "Usernames must be unique"
    assert user1_email != user2_email, "Emails must be unique"
    password = "testpass"
    await register_user(async_client, user1_username, user1_email, password)
    await register_user(async_client, user2_username, user2_email, password)
    login_resp = await login_user(async_client, user1_email, password)
    token = login_resp.json()["user"]["token"]
    resp = await async_client.post(
        f"/profiles/{user2_username}/follow",
        headers={"Authorization": f"Token {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["profile"]
    assert data["username"] == user2_username
    assert data["following"] is True


@pytest.mark.asyncio
async def test_follow_profile_cannot_follow_self(
    async_client: AsyncClient, user_read_factory
) -> None:
    """
    GIVEN a registered user
    WHEN the user tries to follow themselves
    THEN the API returns 400
    """
    user = user_read_factory.build()
    user_data = user.model_dump()
    user_username = user_data["username"]
    user_email = user_data["email"]
    password = "testpass"
    await register_user(async_client, user_username, user_email, password)
    login_resp = await login_user(async_client, user_email, password)
    token = login_resp.json()["user"]["token"]
    resp = await async_client.post(
        f"/profiles/{user_username}/follow",
        headers={"Authorization": f"Token {token}"},
    )
    assert resp.status_code == 400
    assert "cannot follow yourself" in resp.text.lower()


@pytest.mark.asyncio
async def test_follow_profile_not_found(async_client: AsyncClient, user_read_factory) -> None:
    """
    GIVEN a registered user
    WHEN the user tries to follow a non-existent user
    THEN the API returns 404
    """
    user = user_read_factory.build()
    user_data = user.model_dump()
    user_username = user_data["username"]
    user_email = user_data["email"]
    password = "testpass"
    await register_user(async_client, user_username, user_email, password)
    login_resp = await login_user(async_client, user_email, password)
    token = login_resp.json()["user"]["token"]
    resp = await async_client.post(
        "/profiles/nonexistentuser/follow",
        headers={"Authorization": f"Token {token}"},
    )
    assert resp.status_code == 404
    assert "not found" in resp.text.lower()


@pytest.mark.asyncio
async def test_unfollow_profile_success(async_client: AsyncClient, user_read_factory) -> None:
    """
    GIVEN two registered users and one follows the other
    WHEN the follower unfollows the followee
    THEN the API returns 200 and the profile shows following=False
    """
    user1 = user_read_factory.build(username="user1_unfollow", email="user1_unfollow@example.com")
    user2 = user_read_factory.build(username="user2_unfollow", email="user2_unfollow@example.com")
    user1_data = user1.model_dump()
    user2_data = user2.model_dump()
    user1_username = user1_data["username"]
    user1_email = user1_data["email"]
    user2_username = user2_data["username"]
    user2_email = user2_data["email"]
    password = "testpass"
    await register_user(async_client, user1_username, user1_email, password)
    await register_user(async_client, user2_username, user2_email, password)
    login_resp = await login_user(async_client, user1_email, password)
    token = login_resp.json()["user"]["token"]
    # Follow first
    await async_client.post(
        f"/profiles/{user2_username}/follow",
        headers={"Authorization": f"Token {token}"},
    )
    # Now unfollow
    resp = await async_client.delete(
        f"/profiles/{user2_username}/follow",
        headers={"Authorization": f"Token {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["profile"]
    assert data["username"] == user2_username
    assert data["following"] is False


@pytest.mark.asyncio
async def test_unfollow_profile_not_following(async_client: AsyncClient, user_read_factory) -> None:
    """
    GIVEN two registered users and one is not following the other
    WHEN the follower tries to unfollow the followee
    THEN the API returns 200 and the profile shows following=False
    """
    user1 = user_read_factory.build(username="user1_unfollow2", email="user1_unfollow2@example.com")
    user2 = user_read_factory.build(username="user2_unfollow2", email="user2_unfollow2@example.com")
    user1_data = user1.model_dump()
    user2_data = user2.model_dump()
    user1_username = user1_data["username"]
    user1_email = user1_data["email"]
    user2_username = user2_data["username"]
    user2_email = user2_data["email"]
    password = "testpass"
    await register_user(async_client, user1_username, user1_email, password)
    await register_user(async_client, user2_username, user2_email, password)
    login_resp = await login_user(async_client, user1_email, password)
    token = login_resp.json()["user"]["token"]
    # Unfollow without following first
    resp = await async_client.delete(
        f"/profiles/{user2_username}/follow",
        headers={"Authorization": f"Token {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["profile"]
    assert data["username"] == user2_username
    assert data["following"] is False


@pytest.mark.asyncio
async def test_unfollow_profile_cannot_unfollow_self(
    async_client: AsyncClient, user_read_factory
) -> None:
    """
    GIVEN a registered user
    WHEN the user tries to unfollow themselves
    THEN the API returns 400
    """
    user = user_read_factory.build()
    user_data = user.model_dump()
    user_username = user_data["username"]
    user_email = user_data["email"]
    password = "testpass"
    await register_user(async_client, user_username, user_email, password)
    login_resp = await login_user(async_client, user_email, password)
    token = login_resp.json()["user"]["token"]
    resp = await async_client.delete(
        f"/profiles/{user_username}/follow",
        headers={"Authorization": f"Token {token}"},
    )
    assert resp.status_code == 400
    assert "cannot unfollow yourself" in resp.text.lower()


@pytest.mark.asyncio
async def test_unfollow_profile_not_found(async_client: AsyncClient, user_read_factory) -> None:
    """
    GIVEN a registered user
    WHEN the user tries to unfollow a non-existent user
    THEN the API returns 404
    """
    user = user_read_factory.build()
    user_data = user.model_dump()
    user_username = user_data["username"]
    user_email = user_data["email"]
    password = "testpass"
    await register_user(async_client, user_username, user_email, password)
    login_resp = await login_user(async_client, user_email, password)
    token = login_resp.json()["user"]["token"]
    resp = await async_client.delete(
        "/profiles/nonexistentuser/follow",
        headers={"Authorization": f"Token {token}"},
    )
    assert resp.status_code == 404
    assert "not found" in resp.text.lower()
