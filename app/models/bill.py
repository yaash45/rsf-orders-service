from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from . import Identifiable, TimeStamped


class BillBase(BaseModel):
    amount: float = Field(ge=0.0)
    image_url: HttpUrl | None = None
    paid: bool | None = Field(default=False)


class BillCreate(BillBase, TimeStamped): ...


class BillUpdatePaid(BaseModel):
    paid: bool


class BillUpdateAmount(BaseModel):
    amount: float = Field(ge=0.0)


class BillUpdateImage(BaseModel):
    image_url: HttpUrl


class BillPublic(BillBase, Identifiable, TimeStamped):
    model_config = ConfigDict(from_attributes=True)
