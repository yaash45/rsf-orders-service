from logging import getLogger
from typing import Iterator

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.user import UserService

logger = getLogger(__name__)

router = APIRouter(prefix="/v0")


def get_user_service(db: Session = Depends(get_db)) -> Iterator[UserService]:
    """
    Returns a UserService instance using the provided database session.

    The UserService instance is used to encapsulate database operations
    related to users.
    """
    yield UserService(db=db)
