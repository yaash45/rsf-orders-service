from uuid import UUID as py_UUID

from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.schemas.base import BaseSchemaDb


class PaymentDb(BaseSchemaDb):
    """
    Schema representing the payments made towards an order.

    Each bill can be paid in multiple installments.
    """

    __tablename__ = "payments"

    # the amount paid in this single payment
    amount: Mapped[float] = mapped_column(Float, nullable=False)

    # the bill that this payment was made towards
    bill_id: Mapped[py_UUID] = mapped_column(ForeignKey("bills.id"))
