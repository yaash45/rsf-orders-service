from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class ProductCreate(BaseModel):
    name: str
    available_sizes: list[ProductSize]
    description: str | None = None
    image: HttpUrl | None = None


class Product(ProductCreate):
    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)


class ProductSize(str, Enum):
    TEN_ML = "10 mL"
    THIRTY_ML = "30 mL"
    SIXTY_ML = "60 mL"
    HUNDRED_ML = "100 mL"
    TWO_HUNDRED_ML = "200 mL"
    FIVE_HUNDRED_ML = "500 mL"
    ONE_L = "1 L"
    TWO_L = "2 L"
    FIVE_L = "5 L"
    TEN_L = "10 L"


class Catalog(BaseModel):
    items: list[UUID]
