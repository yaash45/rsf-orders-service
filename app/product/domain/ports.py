from typing import Iterable, Protocol
from uuid import UUID

from .models import (
    ProductCreate,
    ProductPublic,
    ProductVariantCreate,
    ProductVariantPublic,
)


class ProductPort(Protocol):
    def fetch_one(self, product_id: UUID) -> ProductPublic | None:
        """
        Fetches a single product
        """
        ...

    def fetch_variants(self, product_id: UUID) -> Iterable[ProductVariantPublic]:
        """
        Fetches all the available variants for a product
        """
        ...

    def fetch_id_map(self) -> dict[UUID, str]:
        """
        Returns a map of product ids and their name
        """
        ...

    def add_products(self, products: list[ProductCreate]) -> Iterable[ProductPublic]:
        """
        Add products to the backend
        """
        ...

    def add_variants(
        self, product_id: UUID, variants: list[ProductVariantCreate]
    ) -> Iterable[ProductVariantPublic]:
        """
        Add available variants for a product
        """
        ...
