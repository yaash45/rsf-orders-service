from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, PositiveFloat


class PaymentMethod(str, Enum):
    CASH = "Cash"
    UPI = "UPI"
    BANK = "Bank"


class PaymentCreate(BaseModel):
    amount: PositiveFloat
    client_id: UUID
    order_id: UUID
    method: PaymentMethod


class Payment(PaymentCreate):
    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)
