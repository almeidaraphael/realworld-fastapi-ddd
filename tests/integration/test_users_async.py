import pytest
from httpx import AsyncClient

from app.shared.jwt import create_access_token
from tests.helpers import login_user, register_user


@pytest.mark.asyncio
async def test_create_user_success(async_client: AsyncClient, user_factory) -> None:
    """
    GIVEN valid user data
    WHEN registering a new user
    THEN the API returns 201 and user data with token
    """
    user = user_factory.build()
    password = "testpassasync"
    response = await async_client.post(
        "/users",
        json={
            "user": {
                "username": user.username,
                "email": user.email,
                "password": password,
            }
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert data["user"]["username"] == user.username
    assert data["user"]["email"] == user.email
    assert "token" in data["user"]


@pytest.mark.asyncio
async def test_create_user_duplicate(async_client: AsyncClient) -> None:
    """
    GIVEN a user already exists
    WHEN registering with the same username/email
    THEN the API returns 400 and error detail
    """
    await register_user(
        async_client, "dupuser", "dup@example.com", "testpass"
    )  # First registration
    resp = await register_user(
        async_client, "dupuser", "dup@example.com", "testpass"
    )  # Duplicate registration
    assert resp.status_code == 400
    data = resp.json()
    assert "detail" in data
    assert "registered" in data["detail"]


@pytest.mark.asyncio
async def test_login_user_success(async_client: AsyncClient) -> None:
    """
    GIVEN a registered user
    WHEN logging in with correct credentials
    THEN the API returns 200 and user data with token
    """
    await register_user(async_client, "loginuser", "login@example.com", "loginpass")
    resp = await login_user(async_client, "login@example.com", "loginpass")
    assert resp.status_code == 200
    data = resp.json()
    assert "user" in data
    assert data["user"]["email"] == "login@example.com"
    assert "token" in data["user"]


@pytest.mark.asyncio
async def test_login_user_invalid(async_client: AsyncClient) -> None:
    """
    GIVEN no user exists for credentials
    WHEN logging in with invalid credentials
    THEN the API returns 400 and error detail
    """
    resp = await login_user(async_client, "notfound@example.com", "wrongpass")
    assert resp.status_code == 400
    data = resp.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_current_user_success(async_client: AsyncClient) -> None:
    """
    GIVEN a logged-in user
    WHEN requesting /user with valid token
    THEN the API returns 200 and user data
    """
    await register_user(async_client, "meuser", "me@example.com", "mepass")
    login_resp = await login_user(async_client, "me@example.com", "mepass")
    token = login_resp.json()["user"]["token"]
    resp = await async_client.get("/user", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["email"] == "me@example.com"
    assert data["user"]["username"] == "meuser"


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(async_client: AsyncClient) -> None:
    """
    GIVEN no authentication
    WHEN requesting /user
    THEN the API returns 401
    """
    resp = await async_client.get("/user")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_user_success(async_client: AsyncClient) -> None:
    """
    GIVEN a logged-in user
    WHEN updating bio and image
    THEN the API returns 200 and updated user data
    """
    await register_user(async_client, "updateuser", "update@example.com", "updatepass")
    login_resp = await login_user(async_client, "update@example.com", "updatepass")
    token = login_resp.json()["user"]["token"]
    resp = await async_client.put(
        "/user",
        headers={"Authorization": f"Bearer {token}"},
        json={"user": {"bio": "new bio", "image": "http://img.com/new.png"}},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["bio"] == "new bio"
    assert data["user"]["image"] == "http://img.com/new.png"
    assert data["user"]["email"] == "update@example.com"


@pytest.mark.asyncio
async def test_update_user_partial(async_client: AsyncClient) -> None:
    """
    GIVEN a logged-in user
    WHEN updating only the username
    THEN the API returns 200 and updated username
    """
    await register_user(async_client, "partialuser", "partial@example.com", "partialpass")
    login_resp = await login_user(async_client, "partial@example.com", "partialpass")
    token = login_resp.json()["user"]["token"]
    resp = await async_client.put(
        "/user",
        headers={"Authorization": f"Bearer {token}"},
        json={"user": {"username": "partialuser2"}},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["username"] == "partialuser2"
    assert data["user"]["email"] == "partial@example.com"


@pytest.mark.asyncio
async def test_update_user_unauthorized(async_client: AsyncClient) -> None:
    """
    GIVEN no authentication
    WHEN updating user
    THEN the API returns 401
    """
    resp = await async_client.put(
        "/user",
        json={"user": {"bio": "should fail"}},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token_payload(async_client: AsyncClient) -> None:
    """
    GIVEN a token missing 'sub' claim
    WHEN requesting /user with this token
    THEN the API returns 401 and error detail
    """
    token = create_access_token({"foo": "bar"})
    resp = await async_client.get(
        "/user",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid authentication credentials"


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(async_client: AsyncClient) -> None:
    """
    GIVEN a token with valid 'sub' but user does not exist
    WHEN requesting /user with this token
    THEN the API returns 401 and error detail
    """
    token = create_access_token({"sub": "ghost@example.com"})
    resp = await async_client.get(
        "/user",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "User not found"
