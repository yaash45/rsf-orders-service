from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v0 import product, user
from app.core.config import Environments, config
from app.core.logging import getLogger
from app.db import Base, engine

logger = getLogger(__name__)


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

app.include_router(product.router, prefix="/product", tags=["product"])
app.include_router(user.router, prefix="/users", tags=["users"])
