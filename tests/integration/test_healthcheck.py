from httpx import AsyncClient


async def test_healthcheck(async_client: AsyncClient) -> None:
    """
    GIVEN a running FastAPI application
    WHEN the /healthcheck endpoint is called
    THEN it should return status 200 and a JSON body {"status": "ok"}
    """
    response = await async_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
