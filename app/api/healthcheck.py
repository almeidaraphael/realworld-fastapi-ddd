from fastapi import APIRouter

router = APIRouter()


@router.get("/healthcheck", tags=["Healthcheck"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
