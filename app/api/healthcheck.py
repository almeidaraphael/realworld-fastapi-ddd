from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Healthcheck"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
