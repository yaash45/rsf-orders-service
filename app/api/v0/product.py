from typing import Iterator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.product import (
    ProductCreate,
    ProductPublic,
    ProductVariantCreate,
    ProductVariantPublic,
)
from app.services.product import ProductService

router = APIRouter(prefix="/v0")


def get_product_service(db: Session = Depends(get_db)) -> Iterator[ProductService]:
    """
    Returns an instance of ProductService that can be used to interact with the database.

    Yields an instance of ProductService that is bound to the provided database session.
    """
    yield ProductService(db=db)


@router.get(
    "/products/{product_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Product not found",
        },
    },
    response_model=ProductPublic,
    status_code=status.HTTP_200_OK,
)
def get_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
) -> ProductPublic:
    """
    Retrieves a single Product queried by id

    Args:
        product_id (UUID): The ID of the Product to retrieve

    Returns:
        ProductPublic: The Product with the given ID, or None if no such product exists

    Raises:
        HttpException with a 404 status if the product cannot be found
    """
    product = service.get_product(product_id=product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


@router.post(
    "/products",
    response_model=list[ProductPublic],
    status_code=status.HTTP_201_CREATED,
)
def register_products(
    request: list[ProductCreate],
    service: ProductService = Depends(get_product_service),
) -> list[ProductPublic]:
    """
    Registers a list of products with their respective variants.

    Args:
        request (list[ProductCreate]): A list of ProductCreate objects to register.

    Returns:
        list[ProductPublic]: A list of newly registered products with their respective variants.
    """
    return service.register_products(request=request)


@router.get(
    "/products/id_map",
    response_model=dict[UUID, str],
    status_code=status.HTTP_200_OK,
)
def get_product_id_map(
    service: ProductService = Depends(get_product_service),
) -> dict[UUID, str]:
    """
    Retrieves a dictionary mapping product IDs to their respective names.

    Returns:
        dict[UUID, str]: A dictionary mapping product IDs to their names
    """
    return service.get_product_id_map()


@router.get(
    "/products/{product_id}/variants",
    response_model=list[ProductVariantPublic],
    status_code=status.HTTP_200_OK,
)
def get_variants_for_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
) -> list[ProductVariantPublic]:
    """
    Retrieves a list of ProductVariantPublic objects for a given product ID.

    Args:
        product_id (UUID): The ID of the product to retrieve variants for.

    Returns:
        list[ProductVariantPublic]: A list of ProductVariantPublic objects for the given product ID.
    """
    return service.get_variants_for_product(product_id=product_id)


@router.post(
    "/products/{product_id}/variants",
    response_model=list[ProductVariantPublic],
    status_code=status.HTTP_201_CREATED,
)
def add_available_variants(
    product_id: UUID,
    variants: list[ProductVariantCreate],
    service: ProductService = Depends(get_product_service),
) -> list[ProductVariantPublic]:
    """
    Adds a list of ProductVariantCreate objects as available variants for a given product ID.

    Args:
        product_id (UUID): The ID of the product to add variants for.
        variants (list[ProductVariantCreate]): A list of ProductVariantCreate objects to add as available variants.

    Returns:
        list[ProductVariantPublic]: A list of ProductVariantPublic objects for the given product ID.
    """
    return service.add_available_variants(product_id=product_id, variants=variants)
