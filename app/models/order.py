from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, NonNegativeFloat, PositiveInt

from .product import ProductSize


class OrderStatus(str, Enum):
    PENDING = "Pending"
    FULFILLED = "Fulfilled"
    PAID = "Paid"


class OrderCreate(BaseModel):
    client_id: UUID
    products: dict[UUID, dict[ProductSize, PositiveInt]] = {}


class Order(OrderCreate):
    id: UUID = Field(default_factory=uuid4)

    # default order state is pending
    status: OrderStatus = OrderStatus.PENDING

    bill_id: UUID | None = None

    # important dates
    created: datetime = Field(default_factory=datetime.now)
    fulfilled: datetime | None = None
    paid: datetime | None = None

    # tracking remaining payments
    total: NonNegativeFloat | None = None
