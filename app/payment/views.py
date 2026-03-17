from logging import getLogger
from typing import Iterator

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.payment.service import PaymentService

logger = getLogger(__name__)

router_v0 = APIRouter(prefix="/v0")


def get_payment_service(db: Session = Depends(get_db)) -> Iterator[PaymentService]:
    """
    Returns a UserService instance using the provided database session.

    The UserService instance is used to encapsulate database operations
    related to users.
    """
    yield PaymentService(db=db)
