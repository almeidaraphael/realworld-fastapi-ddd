import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.healthcheck import router as healthcheck_router
from app.api.profiles import router as profiles_router
from app.api.users import router as users_router


# Configure logging to work both locally and in Docker
def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
    )


setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(healthcheck_router)
app.include_router(users_router)
app.include_router(profiles_router)
