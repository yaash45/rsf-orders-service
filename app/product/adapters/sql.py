from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..domain.models import (
    ProductCreate,
    ProductPublic,
    ProductVariantCreate,
    ProductVariantPublic,
)
from ..domain.ports import ProductPort
from ..schemas import Product, ProductVariant


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
