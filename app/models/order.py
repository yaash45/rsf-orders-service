from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from . import Identifiable, TimeStamped
from .product import ProductSize


class OrderStatus(str, Enum):
    PENDING = "Pending"
    FULFILLED = "Fulfilled"
    PAID = "Paid"


class OrderBase(BaseModel):
    # status and payments
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    payments: list[UUID] = Field(default_factory=list)

    # identifiers
    bill_id: UUID | None = None
    user_id: UUID

    # products associated with Order
    products: dict[UUID, dict[ProductSize, PositiveInt]] = Field(default_factory=dict)


class OrderCreate(OrderBase, TimeStamped): ...


class OrderPublic(OrderBase, Identifiable, TimeStamped):
    model_config = ConfigDict(from_attributes=True)


# class Order(OrderCreate):
#     id: UUID = Field(default_factory=uuid4)

#     # default order state is pending
#     status: OrderStatus = OrderStatus.PENDING

#     bill_id: UUID | None = None

#     # important dates
#     created: datetime = Field(default_factory=datetime.now)
#     fulfilled: datetime | None = None
#     paid: datetime | None = None

#     # tracking remaining payments
#     total: NonNegativeFloat | None = None
