from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, PositiveFloat


class PaymentCreate(BaseModel):
    amount: PositiveFloat
    client: UUID


class Payment(PaymentCreate):
    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)
