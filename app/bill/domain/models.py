from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.core.models import Identifiable, TimeStamped


class BillBase(BaseModel):
    amount: float = Field(ge=0.0)
    currency: str = Field(default="INR")
    image_url: HttpUrl | None = None
    paid: bool = Field(default=False)
    order_id: UUID


class BillCreate(BillBase, TimeStamped):
    """
    Creation request for a new bill for an order
    """


class BillPublic(BillBase, Identifiable, TimeStamped):
    """
    Public-facing general bill model
    """

    model_config = ConfigDict(from_attributes=True)
