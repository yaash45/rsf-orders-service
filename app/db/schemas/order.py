from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID as py_UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.db.schemas import BaseSchemaDb

if TYPE_CHECKING:
    from .bill import BillDb


class OrderItemDb(Base):
    """
    Represents an item that is part of an order, specifying the product,
    its variant, and quantity
    """

    __tablename__ = "order_items"

    # the order that this item is associated with
    order_id: Mapped[py_UUID] = mapped_column(
        ForeignKey("orders.id"),
        primary_key=True,
    )

    # the product and its variant that is being ordered
    product_variant: Mapped[py_UUID] = mapped_column(
        ForeignKey("product_variants.id"),
        primary_key=True,
    )

    # quantity of the product ordered
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)


class OrderDb(BaseSchemaDb):
    """
    Represents the orders made by various users
    """

    __tablename__ = "orders"

    # order status related fields
    status: Mapped[str] = mapped_column(String(9), nullable=False)
    status_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # refer to the user that placed the order
    user_id: Mapped[py_UUID] = mapped_column(ForeignKey("users.id"))

    # tracks which products were ordered, and how many
    items: Mapped[list["OrderItemDb"]] = relationship()

    # bill associated with the order
    bill: Mapped["BillDb | None"] = relationship(
        "BillDb",
        uselist=False,
        back_populates="order",
    )
