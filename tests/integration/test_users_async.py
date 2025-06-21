import pytest
from httpx import AsyncClient

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
