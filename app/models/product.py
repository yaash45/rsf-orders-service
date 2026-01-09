from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from . import Identifiable, TimeStamped


class ProductVariantBase(BaseModel):
    """
    Base model describing a specific product variant's properties
    """

    size: str
    kind: str


class ProductVariantCreate(ProductVariantBase):
    """
    Creation request model for a product variant
    """


class ProductVariantPublic(ProductVariantBase, Identifiable):
    """
    Public-facing specific product variant model
    """

    product_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    """
    Base representation of a general product
    """

    name: str
    description: str | None = None
    available_variants: list[ProductVariantBase] = Field(default_factory=list)


class ProductCreate(ProductBase, TimeStamped):
    """
    Creation request model for a product
    """


class ProductPublic(ProductBase, Identifiable, TimeStamped):
    """
    Public-facing general product model
    """

    model_config = ConfigDict(from_attributes=True)
