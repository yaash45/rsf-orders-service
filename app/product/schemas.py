from uuid import UUID as py_UUID

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.db.schemas import BaseSchemaDb


class ProductVariantDb(Base):
    """
    Represents the specific variant of a product in the system
    """

    __tablename__ = "product_variants"

    # identify a variant and it's associated product using a UUID
    id: Mapped[py_UUID] = mapped_column(UUID, primary_key=True)

    # a nice label (e.g. "30 mL", "10 mL", etc.)
    size: Mapped[str] = mapped_column(String, nullable=False)

    # the kind of product (e.g. bottle, roll-on, spray, can, etc.)
    kind: Mapped[str] = mapped_column(String, nullable=False)

    # the product specified by this variant
    product_id: Mapped[py_UUID] = mapped_column(ForeignKey("products.id"))

    def __repr__(self):
        return f"ProductVariantDb(size={self.size}, kind={self.kind}, product_id={self.product_id}) at {id(self)}"


class ProductDb(BaseSchemaDb):
    """
    Represents a product registered in the system
    """

    __tablename__ = "products"

    # basic information
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    # available variants
    available_variants: Mapped[list["ProductVariantDb"]] = relationship()

    def __repr__(self):
        return f"ProductDb(name={self.name}, description={self.description}, available_variants={self.available_variants}) at {id(self)}"
