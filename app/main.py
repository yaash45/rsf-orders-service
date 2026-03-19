from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import bill, order, payment, product, user
from app.config import Environments, config
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

app.include_router(bill.router_v0, tags=["bills"])
app.include_router(order.router_v0, tags=["orders"])
app.include_router(payment.router_v0, tags=["payments"])
app.include_router(product.router_v0, tags=["products"])
app.include_router(user.router_v0, tags=["users"])


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
