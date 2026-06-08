from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from uuid import UUID

from sqlalchemy import UUID as sql_UUID
from sqlalchemy import ForeignKey, Integer, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.db import Base, BaseSchema

from ..domain.models import (
    ProductCreate,
    ProductPublic,
    ProductVariantCreate,
    ProductVariantPublic,
)
from ..domain.ports import ProductPort


class ProductVariant(Base):
    """
    Represents the specific variant of a product in the system
    """

    __tablename__ = "product_variants"

    # identify a variant and it's associated product using a UUID
    id: Mapped[UUID] = mapped_column(sql_UUID, primary_key=True)

    # the product variant's size, without the unit
    size: Mapped[int] = mapped_column(Integer, nullable=False)

    # unit for the size value
    unit: Mapped[str] = mapped_column(String, nullable=False)

    # the kind of product (e.g. bottle, roll-on, spray, can, etc.)
    kind: Mapped[str] = mapped_column(String, nullable=False)

    # the product specified by this variant
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))

    def __repr__(self):
        return f"ProductVariant(size={self.size}, kind={self.kind}, product_id={self.product_id}) at {id(self)}"


class Product(BaseSchema):
    """
    Represents a product registered in the system
    """

    __tablename__ = "products"

    # basic information
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    # available variants
    available_variants: Mapped[list["ProductVariant"]] = relationship()

    def __repr__(self):
        return f"Product(name={self.name}, description={self.description}, available_variants={self.available_variants}) at {id(self)}"


@dataclass
class SqlProductAdapter(ProductPort):
    db: Session

    def fetch_one(self, product_id: UUID) -> ProductPublic | None:
        return self.db.get(Product, product_id)

    def fetch_id_map(self) -> dict[UUID, str]:
        return {p.id: p.name for p in self.db.query(Product).all()}

    def fetch_variants(self, product_id: UUID) -> Iterable[ProductVariantPublic]:
        return (
            self.db.execute(
                select(ProductVariant).where(ProductVariant.product_id == product_id)
            )
            .scalars()
            .all()
        )

    def add_products(self, products: list[ProductCreate]) -> Iterable[ProductPublic]:
        result: list[ProductPublic] = []

        for product_creation in products:
            new_product = ProductPublic(**product_creation.model_dump())

            db_product = Product(
                id=new_product.id,
                created=new_product.created,
                modified=new_product.modified,
                name=new_product.name,
                description=new_product.description,
            )

            for variant in new_product.available_variants:
                public_variant = ProductVariantPublic(
                    **variant.model_dump(),
                    product_id=new_product.id,
                )

                db_variant = ProductVariant(
                    id=public_variant.id,
                    size=public_variant.size,
                    unit=public_variant.unit.value,
                    kind=public_variant.kind,
                    product_id=public_variant.product_id,
                )

                db_product.available_variants.append(db_variant)

                self.db.add(db_variant)

            self.db.add(db_product)

            result.append(new_product)

        self.db.commit()

        return result

    def add_variants(
        self, product_id: UUID, variants: list[ProductVariantCreate]
    ) -> Iterable[ProductVariantPublic]:
        result: list[ProductVariantPublic] = []

        for variant in variants:
            new_variant = ProductVariantPublic(
                **variant.model_dump(),
                product_id=product_id,
            )
            db_variant = ProductVariant(
                id=new_variant.id,
                size=new_variant.size,
                unit=new_variant.unit.value,
                kind=new_variant.kind,
                product_id=new_variant.product_id,
            )
            self.db.add(db_variant)
            result.append(new_variant)

        product: Product | None = self.db.get(Product, product_id)

        if product is None:
            raise ValueError(f"Product with ID {product_id} not found")

        # update the product modified timestamp since we updated it's available variants
        product.modified = datetime.now(timezone.utc)

        self.db.commit()

        return result
