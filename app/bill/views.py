from typing import Iterator

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app.bill.adapters import BillSqlAdapter
from app.bill.domain.models import BillCreate, BillPublic
from app.bill.service import BillService
from app.db import get_db

router_v0 = APIRouter(prefix="/v0")


def get_bill_service(db: Session = Depends(get_db)) -> Iterator[BillService]:
    """
    Returns a BillService instance using the provided database session.

    The BillService instance is used to encapsulate database operations
    related to bills.
    """
    yield BillService.instance(port=BillSqlAdapter(db))


@router_v0.post("/bills/")
def issue_bill(
    request: BillCreate,
    service: BillService = Depends(get_bill_service),
) -> BillPublic:
    return service.issue_bill(request=request)
