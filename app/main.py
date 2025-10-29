from fastapi import FastAPI

from .routes import product, user

app = FastAPI()

app.include_router(product.router, prefix="/product", tags=["product"])
app.include_router(user.router, prefix="/user", tags=["user"])
