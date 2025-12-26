from typing import TYPE_CHECKING
from uuid import UUID as py_UUID

from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.schemas import BaseSchemaDb

if TYPE_CHECKING:
    from .order import OrderDb
    from .payment import PaymentDb


class BillDb(BaseSchemaDb):
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
    order: Mapped["OrderDb"] = relationship("OrderDb", back_populates="bill")

    # track all payments made towards this bill
    payments: Mapped[list["PaymentDb"]] = relationship()
