# ruff: noqa: E402

from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.user import UserModel  # noqa: F401
