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
    client: UUID
    products: dict[UUID, dict[ProductSize, PositiveInt]] = {}


class Order(OrderCreate):
    id: UUID = Field(default_factory=uuid4)
    status: OrderStatus = OrderStatus.PENDING  # default order state is pending

    bill: UUID | None = None

    # important dates
    created: datetime = Field(default_factory=datetime.now)
    fulfilled: datetime | None = None
    paid: datetime | None = None

    # tracking remaining payments
    total: NonNegativeFloat | None = None
    payments: list[UUID] = []
