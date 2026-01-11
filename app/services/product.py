from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from app.core.logging import get_logger
from app.db.schemas import ProductDb, ProductVariantDb
from app.models.product import (
    ProductCreate,
    ProductPublic,
    ProductVariantCreate,
    ProductVariantPublic,
)

from . import BaseService

logger = get_logger(__name__)


class ProductService(BaseService):
    """
    Service meant for product-based interactions
    """

    def get_product(self, product_id: UUID) -> ProductPublic | None:
        """
        Retrieves a product by its ID.

        Args:
            product_id (UUID): The ID of the product to retrieve.

        Returns:
            ProductPublic: The product with the given ID, or None if no such product exists.
        """
        return self.db.get(ProductDb, product_id)

    def register_products(self, request: list[ProductCreate]) -> list[ProductPublic]:
        """
        Registers a list of products with their respective variants.

        Args:
            request (list[ProductCreate]): A list of ProductCreate objects to register.

        Returns:
            list[ProductPublic]: A list of newly registered products with their respective variants.
        """
        result: list[ProductPublic] = []

        for product_creation in request:
            new_product = ProductPublic(**product_creation.model_dump())

            db_product = ProductDb(
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

                db_variant = ProductVariantDb(
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

    def get_product_id_map(self) -> dict[UUID, str]:
        """
        Returns a dictionary mapping product IDs to their respective names.

        Returns:
            dict[UUID, str]: A dictionary mapping product IDs to their names
        """
        return {p.id: p.name for p in self.db.query(ProductDb).all()}

    def get_variants_for_product(self, product_id: UUID) -> list[ProductVariantPublic]:
        """
        Retrieves a list of ProductVariantPublic objects for a given product ID.

        Args:
            product_id (UUID): The ID of the product to retrieve variants for.

        Returns:
            list[ProductVariantPublic]: A list of ProductVariantPublic objects for the given product ID.
        """
        return list(
            self.db.execute(
                select(ProductVariantDb).where(
                    ProductVariantDb.product_id == product_id
                )
            )
            .scalars()
            .all()
        )

    def add_available_variants(
        self, product_id: UUID, variants: list[ProductVariantCreate]
    ) -> list[ProductVariantPublic]:
        """
        Adds a list of ProductVariantCreate objects as available variants for a given product ID.

        Args:
            product_id (UUID): The ID of the product to add variants for.
            variants (list[ProductVariantCreate]): A list of ProductVariantCreate objects to add as available variants.
        """
        result: list[ProductVariantPublic] = []

        for variant in variants:
            new_variant = ProductVariantPublic(
                **variant.model_dump(),
                product_id=product_id,
            )
            db_variant = ProductVariantDb(
                id=new_variant.id,
                size=new_variant.size,
                kind=new_variant.kind,
                product_id=new_variant.product_id,
            )
            self.db.add(db_variant)
            result.append(new_variant)

        product: ProductDb | None = self.db.get(ProductDb, product_id)

        if product is None:
            raise ValueError(f"Product with ID {product_id} not found")

        # update the product modified timestamp since we updated it's available variants
        product.modified = datetime.now(timezone.utc)

        self.db.commit()

        return result
