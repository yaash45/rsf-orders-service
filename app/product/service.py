from dataclasses import dataclass
from uuid import UUID

from app.core.logging import get_logger
from app.product.domain.models import (
    ProductCreate,
    ProductPublic,
    ProductVariantCreate,
    ProductVariantPublic,
)
from app.product.domain.port import ProductPort

logger = get_logger(__name__)


@dataclass
class ProductService:
    """
    Service meant for product-based interactions
    """

    port: ProductPort

    @classmethod
    def instance(cls, port: ProductPort) -> "ProductService":
        return cls(port=port)

    def get_product(self, product_id: UUID) -> ProductPublic | None:
        """
        Retrieves a product by its ID.

        Args:
            product_id (UUID): The ID of the product to retrieve.

        Returns:
            ProductPublic: The product with the given ID, or None if no such product exists.
        """
        return self.port.fetch_one(product_id=product_id)

    def register_products(self, request: list[ProductCreate]) -> list[ProductPublic]:
        """
        Registers a list of products with their respective variants.

        Args:
            request (list[ProductCreate]): A list of ProductCreate objects to register.

        Returns:
            list[ProductPublic]: A list of newly registered products with their respective variants.
        """
        return list(self.port.add_products(products=request))

    def get_product_id_map(self) -> dict[UUID, str]:
        """
        Returns a dictionary mapping product IDs to their respective names.

        Returns:
            dict[UUID, str]: A dictionary mapping product IDs to their names
        """
        return self.port.fetch_id_map()

    def get_variants_for_product(self, product_id: UUID) -> list[ProductVariantPublic]:
        """
        Retrieves a list of ProductVariantPublic objects for a given product ID.

        Args:
            product_id (UUID): The ID of the product to retrieve variants for.

        Returns:
            list[ProductVariantPublic]: A list of ProductVariantPublic objects for the given product ID.
        """
        return list(self.port.fetch_variants(product_id=product_id))

    def add_available_variants(
        self, product_id: UUID, variants: list[ProductVariantCreate]
    ) -> list[ProductVariantPublic]:
        """
        Adds a list of ProductVariantCreate objects as available variants for a given product ID.

        Args:
            product_id (UUID): The ID of the product to add variants for.
            variants (list[ProductVariantCreate]): A list of ProductVariantCreate objects to add as available variants.
        """
        return list(self.port.add_variants(product_id=product_id, variants=variants))
