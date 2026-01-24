from typing import Iterator

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.bill import BillService

router = APIRouter(prefix="/v0")


def get_bill_service(db: Session = Depends(get_db)) -> Iterator[BillService]:
    """
    Returns a BillService instance using the provided database session.

    The BillService instance is used to encapsulate database operations
    related to bills.
    """
    yield BillService(db=db)
