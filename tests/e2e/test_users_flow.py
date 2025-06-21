import pytest
from httpx import AsyncClient

from tests.helpers import login_user, register_user


@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient, user_factory) -> None:
    """
    GIVEN valid user data
    WHEN registering a new user
    THEN the API returns 201 and user data with token
    """
    user = user_factory.build()
    user_data = user.model_dump()
    username = user_data["username"]
    email = user_data["email"]
    password = "e2epass"
    resp = await register_user(async_client, username, email, password)
    assert resp.status_code == 201
    reg_data = resp.json()["user"]
    assert reg_data["username"] == username
    assert reg_data["email"] == email
    assert reg_data["token"]


@pytest.mark.asyncio
async def test_login_user_success(async_client: AsyncClient, user_factory) -> None:
    """
    GIVEN a registered user
    WHEN logging in with correct credentials
    THEN the API returns 200 and user data with token
    """
    user = user_factory.build()
    user_data = user.model_dump()
    username = user_data["username"]
    email = user_data["email"]
    password = "e2epass"
    await register_user(async_client, username, email, password)
    login_resp = await login_user(async_client, email, password)
    assert login_resp.status_code == 200
    login_data = login_resp.json()["user"]
    assert login_data["token"]
    assert login_data["email"] == email
    assert login_data["username"] == username


@pytest.mark.asyncio
async def test_get_current_user_success(async_client: AsyncClient, user_factory) -> None:
    """
    GIVEN a logged-in user
    WHEN requesting /user with valid token
    THEN the API returns 200 and user data
    """
    user = user_factory.build()
    user_data = user.model_dump()
    username = user_data["username"]
    email = user_data["email"]
    password = "e2epass"
    await register_user(async_client, username, email, password)
    login_resp = await login_user(async_client, email, password)
    token = login_resp.json()["user"]["token"]
    me_resp = await async_client.get("/user", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()["user"]
    assert me_data["email"] == email
    assert me_data["username"] == username
