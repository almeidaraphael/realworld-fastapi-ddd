import random
import string

import pytest
from httpx import AsyncClient

from tests.helpers import login_user, register_user


def random_suffix(length=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient, user_factory) -> None:
    """
    GIVEN valid user data
    WHEN registering a new user
    THEN the API returns 201 and user data with token
    """
    user = user_factory.build()
    user_data = user.model_dump()
    suffix = random_suffix()
    username = f"{user_data['username']}_{suffix}"
    email = f"{suffix}_{user_data['email']}"
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
    suffix = random_suffix()
    username = f"{user_data['username']}_{suffix}"
    email = f"{suffix}_{user_data['email']}"
    password = "e2epass"
    await register_user(async_client, username, email, password)
    login_resp = await login_user(async_client, email, password)
    assert login_resp.status_code == 200
    login_data = login_resp.json()["user"]
    assert login_data["username"] == username
    assert login_data["email"] == email
    assert login_data["token"]


@pytest.mark.asyncio
async def test_get_current_user_success(async_client: AsyncClient, user_factory) -> None:
    """
    GIVEN a logged-in user
    WHEN requesting /user with valid token
    THEN the API returns 200 and user data
    """
    user = user_factory.build()
    user_data = user.model_dump()
    suffix = random_suffix()
    username = f"{user_data['username']}_{suffix}"
    email = f"{suffix}_{user_data['email']}"
    password = "e2epass"
    await register_user(async_client, username, email, password)
    login_resp = await login_user(async_client, email, password)
    assert login_resp.status_code == 200
    token = login_resp.json()["user"]["token"]
    headers = {"Authorization": f"Token {token}"}
    resp = await async_client.get("/user", headers=headers)
    assert resp.status_code == 200
    user_data = resp.json()["user"]
    assert user_data["username"] == username
    assert user_data["email"] == email


@pytest.mark.asyncio
async def test_update_user_success(async_client: AsyncClient, user_factory) -> None:
    """
    GIVEN a logged-in user
    WHEN updating bio and image
    THEN the API returns 200 and updated user data
    """
    user = user_factory.build()
    user_data = user.model_dump()
    username = user_data["username"]
    email = user_data["email"]
    password = "e2epass"
    await register_user(async_client, username, email, password)
    login_resp = await login_user(async_client, email, password)
    token = login_resp.json()["user"]["token"]
    update_resp = await async_client.put(
        "/user",
        headers={"Authorization": f"Token {token}"},
        json={"user": {"bio": "e2e bio", "image": "http://img.com/e2e.png"}},
    )
    assert update_resp.status_code == 200
    upd_data = update_resp.json()["user"]
    assert upd_data["bio"] == "e2e bio"
    assert upd_data["image"] == "http://img.com/e2e.png"
    assert upd_data["email"] == email
