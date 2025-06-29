from httpx import AsyncClient, Response


async def register_user(
    async_client: AsyncClient, username: str, email: str, password: str
) -> Response:
    resp = await async_client.post(
        "/api/users",
        json={"user": {"username": username, "email": email, "password": password}},
    )
    return resp


async def login_user(async_client: AsyncClient, email: str, password: str) -> Response:
    resp = await async_client.post(
        "/api/users/login",
        json={"user": {"email": email, "password": password}},
    )
    return resp
