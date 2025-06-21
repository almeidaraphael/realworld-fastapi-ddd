from httpx import AsyncClient, Response


async def register_user(
    async_client: AsyncClient, username: str, email: str, password: str
) -> Response:
    resp = await async_client.post(
        "/users",
        json={"user": {"username": username, "email": email, "password": password}},
    )
    return resp
