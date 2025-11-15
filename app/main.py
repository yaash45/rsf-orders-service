from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.db import Base, engine
from app.core.logging import getLogger

from .routes import product, user

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    yield

    logger.info("Shutting down")


app = FastAPI(lifespan=lifespan)

app.include_router(product.router, prefix="/product", tags=["product"])
app.include_router(user.router, prefix="/users", tags=["users"])
