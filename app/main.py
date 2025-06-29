import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.articles import router as articles_router
from app.api.healthcheck import router as healthcheck_router
from app.api.profiles import router as profiles_router
from app.api.tags import router as tags_router
from app.api.users import router as users_router
from app.shared.event_registry import register_all_event_handlers


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
    # Register all event handlers on startup
    register_all_event_handlers()
    logger.info("FastAPI application startup complete")
    yield
    logger.info("FastAPI application shutdown")


app = FastAPI(lifespan=lifespan)

app.include_router(healthcheck_router)
app.include_router(users_router, prefix="/api")
app.include_router(profiles_router, prefix="/api")
app.include_router(articles_router, prefix="/api")
app.include_router(tags_router, prefix="/api")
