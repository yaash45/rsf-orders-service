from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.bill.domain.models import BillPublic
from app.core.models import Identifiable, TimeStamped


class OrderStatus(str, Enum):
    PENDING = "pending"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class OrderItemPublic(BaseModel):
    product_variant_id: UUID
    quantity: int = Field(gt=0)


class OrderBase(BaseModel):
    """
    Model containing base definition of an order
    """

    status: OrderStatus = OrderStatus.PENDING

    status_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    user_id: UUID

    items: list[OrderItemPublic] = Field(default_factory=list)


class OrderCreate(OrderBase, TimeStamped):
    """
    Order creation request model
    """


class OrderPublic(OrderCreate, Identifiable):
    """
    Order model that is returned to the user
    """

    bill: BillPublic | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderUpdateItems(TimeStamped, Identifiable):
    """
    Model to update an existing order's items
    """

    items: list[OrderItemPublic] = Field(default_factory=list)
