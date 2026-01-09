from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v0 import bill, user
from app.core.config import Environments, config
from app.core.logging import get_logger
from app.db import Base, engine

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    yield

    logger.info("Shutting down")


app = FastAPI(
    lifespan=lifespan,
    title=config.APP_NAME,
    version=config.APP_VER,
    docs_url=None if config.ENVIRONMENT == Environments.PROD else "/docs",
    redoc_url=None if config.ENVIRONMENT == Environments.PROD else "/redoc",
)

app.include_router(user.router, tags=["users"])
app.include_router(bill.router, tags=["bills"])
