from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v0 import bill, user
from app.core.config import Environments, config
from app.core.logging import get_logger
from app.db import Base, engine
from app.order import router as order_v0
from app.product import router as product_v0

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

app.include_router(order_v0, tags=["orders"])
app.include_router(user.router, tags=["users"])
app.include_router(bill.router, tags=["bills"])
app.include_router(product_v0, tags=["products"])


@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {"status": "ok"}


@app.get("/info")
async def info():
    """
    Server information endpoint
    """
    return {
        "name": config.APP_NAME,
        "version": config.APP_VER,
    }
