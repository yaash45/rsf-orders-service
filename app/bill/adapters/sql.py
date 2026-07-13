from typing import TYPE_CHECKING
from uuid import UUID as py_UUID

from sqlalchemy import Boolean, Float, ForeignKey, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.bill.domain.models import BillCreate, BillPublic
from app.db import BaseSchema

if TYPE_CHECKING:
    from app.order.adapters.sql import Order
    from app.payment.schemas import Payment

from dataclasses import dataclass

from app.bill.domain.ports import BillPort


class Bill(BaseSchema):
    """
    Database schema representing a bill for an order.
    """

    __tablename__ = "bills"

    # the total bill amount and currency
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    # optional image of the bill copy
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)

    # Flag indicating if the bill has been paid or not
    paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # the order that this bill is associated with
    order_id: Mapped[py_UUID] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        unique=True,  # enforce one bill per order
    )
    order: Mapped["Order"] = relationship("Order", back_populates="bill")

    # track all payments made towards this bill
    payments: Mapped[list["Payment"]] = relationship()


@dataclass
class SqlBillAdapter(BillPort):
    db: Session

    def fetch_for_order(self, order_id: py_UUID) -> BillPublic | None:
        stmt = select(Bill).where(Bill.order_id == order_id)
        return self.db.scalar(stmt)

    def create_bill(self, request: BillCreate) -> BillPublic:
        new_bill = BillPublic(**request.model_dump())

        db_bill = Bill(
            id=new_bill.id,
            created=new_bill.created,
            modified=new_bill.modified,
            amount=new_bill.amount,
            currency=new_bill.currency,
            image_url=new_bill.image_url or None,
            paid=new_bill.paid,
            order_id=new_bill.order_id,
        )

        self.db.add(db_bill)

        return new_bill
