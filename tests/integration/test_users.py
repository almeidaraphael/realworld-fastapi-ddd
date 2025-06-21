import pytest
from httpx import AsyncClient

from tests.helpers import register_user


@pytest.mark.asyncio
async def test_create_user_success(user_factory, async_client: AsyncClient) -> None:
    """
    GIVEN a new user registration request
    WHEN the /users endpoint is called with valid user data
    THEN the API should return 201 (created)
    """
    user = user_factory.build()
    password = "testpass"
    resp = await register_user(async_client, user.username, user.email, password)
    assert resp.status_code == 201
    data = resp.json()
    assert data["user"]["username"] == user.username
    assert data["user"]["email"] == user.email
    assert "token" in data["user"]
