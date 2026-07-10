from typing import Protocol
from uuid import UUID

from app.bill.domain.models import BillCreate, BillPublic


class BillPort(Protocol):
    def fetch_for_order(self, order_id: UUID) -> BillPublic:
        """
        Fetch a bill for a given order
        """

        raise NotImplementedError("not implemented yet")

    def create_bill(self, request: BillCreate) -> BillPublic:
        """
        Create a new bill for an order
        """

        raise NotImplementedError("not implemented yet")
