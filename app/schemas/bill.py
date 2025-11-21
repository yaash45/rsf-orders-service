from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class BillCreate(BaseModel):
    image: HttpUrl


class Bill(BillCreate):
    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)
