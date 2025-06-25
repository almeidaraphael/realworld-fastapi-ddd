from httpx import AsyncClient

from app.shared.jwt import create_access_token
from tests.helpers import login_user, register_user


async def test_create_user_success(async_client: AsyncClient, user_factory) -> None:
    """
    GIVEN valid user data
    WHEN registering a new user
    THEN the API returns 201 and user data with token
    """
    user = user_factory.build()
    password = "testpassasync"
    response = await async_client.post(
        "/api/users",
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


async def test_create_user_duplicate(async_client: AsyncClient) -> None:
    """
    GIVEN a user already exists
    WHEN registering with the same username/email
    THEN the API returns 409 and error detail with error code
    """
    await register_user(
        async_client, "dupuser", "dup@example.com", "testpass"
    )  # First registration
    resp = await register_user(
        async_client, "dupuser", "dup@example.com", "testpass"
    )  # Duplicate registration
    assert resp.status_code == 409
    data = resp.json()
    assert "detail" in data
    assert "UserAlreadyExistsError" in data["detail"]


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


async def test_login_user_invalid(async_client: AsyncClient) -> None:
    """
    GIVEN no user exists for credentials
    WHEN logging in with invalid credentials
    THEN the API returns 401 and error detail with error code
    """
    resp = await login_user(async_client, "notfound@example.com", "wrongpass")
    assert resp.status_code == 401
    data = resp.json()
    assert "detail" in data
    assert "INVALID_CREDENTIALS:" in data["detail"]


async def test_get_current_user_success(async_client: AsyncClient) -> None:
    """
    GIVEN a logged-in user
    WHEN requesting /user with valid token
    THEN the API returns 200 and user data
    """
    await register_user(async_client, "meuser", "me@example.com", "mepass")
    login_resp = await login_user(async_client, "me@example.com", "mepass")
    token = login_resp.json()["user"]["token"]
    resp = await async_client.get("/api/user", headers={"Authorization": f"Token {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["email"] == "me@example.com"
    assert data["user"]["username"] == "meuser"


async def test_get_current_user_unauthorized(async_client: AsyncClient) -> None:
    """
    GIVEN no authentication
    WHEN requesting /user
    THEN the API returns 401
    """
    resp = await async_client.get("/api/user")
    assert resp.status_code == 401


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
        "/api/user",
        headers={"Authorization": f"Token {token}"},
        json={"user": {"bio": "new bio", "image": "http://img.com/new.png"}},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["bio"] == "new bio"
    assert data["user"]["image"] == "http://img.com/new.png"
    assert data["user"]["email"] == "update@example.com"


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
        "/api/user",
        headers={"Authorization": f"Token {token}"},
        json={"user": {"username": "partialuser2"}},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["username"] == "partialuser2"
    assert data["user"]["email"] == "partial@example.com"


async def test_update_user_unauthorized(async_client: AsyncClient) -> None:
    """
    GIVEN no authentication
    WHEN updating user
    THEN the API returns 401
    """
    resp = await async_client.put(
        "/api/user",
        json={"user": {"bio": "should fail"}},
    )
    assert resp.status_code == 401


async def test_get_current_user_invalid_token_payload(async_client: AsyncClient) -> None:
    """
    GIVEN a token missing 'sub' claim
    WHEN requesting /user with this token
    THEN the API returns 401 and error detail
    """
    token = create_access_token({"foo": "bar"})
    resp = await async_client.get(
        "/api/user",
        headers={"Authorization": f"Token {token}"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "INVALID_CREDENTIALS: Invalid authentication credentials"


async def test_get_current_user_user_not_found(async_client: AsyncClient) -> None:
    """
    GIVEN a token with valid 'sub' but user does not exist
    WHEN requesting /user with this token
    THEN the API returns 401 and error detail
    """
    token = create_access_token({"sub": "ghost@example.com"})
    resp = await async_client.get(
        "/api/user",
        headers={"Authorization": f"Token {token}"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "USER_NOT_FOUND: User not found"


async def test_get_current_user_missing_authorization_header(async_client: AsyncClient) -> None:
    """
    GIVEN no Authorization header
    WHEN requesting /user
    THEN the API returns 401 with MISSING_TOKEN error
    """
    resp = await async_client.get("/api/user")
    assert resp.status_code == 401
    data = resp.json()
    assert "MISSING_TOKEN: Missing or invalid Authorization header" in data["detail"]


async def test_get_current_user_invalid_authorization_format(async_client: AsyncClient) -> None:
    """
    GIVEN invalid Authorization header format (not starting with 'Token ')
    WHEN requesting /user
    THEN the API returns 401 with MISSING_TOKEN error
    """
    resp = await async_client.get(
        "/api/user",
        headers={"Authorization": "Bearer invalidformat"},
    )
    assert resp.status_code == 401
    data = resp.json()
    assert "MISSING_TOKEN: Missing or invalid Authorization header" in data["detail"]


async def test_get_current_user_empty_token(async_client: AsyncClient) -> None:
    """
    GIVEN empty token after 'Token ' prefix
    WHEN requesting /user
    THEN the API returns 401 with MISSING_TOKEN error
    """
    resp = await async_client.get(
        "/api/user",
        headers={"Authorization": "Token "},
    )
    assert resp.status_code == 401
    data = resp.json()
    assert "MISSING_TOKEN: Missing or invalid Authorization header" in data["detail"]


async def test_update_user_with_user_not_found_error(async_client: AsyncClient) -> None:
    """
    GIVEN a valid token for a user that doesn't exist in database
    WHEN updating user profile
    THEN the API returns 401 because authentication fails (user not found in DB)
    """
    # Create a token for a non-existent user
    token = create_access_token({"sub": "nonexistent@example.com"})

    update_data = {"user": {"bio": "Updated bio", "image": "https://example.com/new-image.jpg"}}

    resp = await async_client.put(
        "/api/user",
        json=update_data,
        headers={"Authorization": f"Token {token}"},
    )
    assert resp.status_code == 401
    data = resp.json()
    assert "USER_NOT_FOUND: User not found" in data["detail"]
