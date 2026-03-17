from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.models import Identifiable, TimeStamped
from app.models.bill import BillPublic


class OrderStatus(str, Enum):
    PENDING = "Pending"
    FULFILLED = "Fulfilled"
    CANCELLED = "Cancelled"


class OrderBase(BaseModel):
    """
    Model containing base definition of an order
    """

    status: OrderStatus = OrderStatus.PENDING

    status_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    user_id: UUID

    items: dict[UUID, int] = {}


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

    items: dict[UUID, int] = {}
