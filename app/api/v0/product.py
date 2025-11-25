from uuid import UUID

from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from app.exceptions import NotFoundResponse
from app.models.product import (
    Catalog,
    Product,
    ProductCreate,
    ProductSize,
    ProductSummary,
)

router = APIRouter()

catalog = Catalog()


@router.get("/", response_model=list[ProductSummary])
def get_all_products():
    """
    Return a list of all products.

    Returns:
        list[Product]: A list of all products.
    """
    return catalog.values()


@router.get(
    "/{id}/sizes/",
    responses={
        200: {"model": list[ProductSize]},
        404: {"model": NotFoundResponse},
    },
)
def get_available_sizes(id: UUID):
    """
    Return a list of all available sizes for a product.

    Args:
        id (UUID): The ID of the product to retrieve available sizes for.

    Returns:
        list[ProductSize]: A list of all available sizes for the product.

    Raises:
        HTTPException: A 404 error is raised if the product with the given ID is not found.
    """
    if id not in catalog:
        raise HTTPException(status_code=404, detail=f"Product {id} not found")

    return catalog[id].available_sizes


@router.post("/", response_model=Product, status_code=201)
def create_product(request: ProductCreate):
    """
    Create a new product.

    Args:
        request (ProductCreate): The product to create.

    Returns:
        Product: The newly created product.
    """
    new_product = Product(**request.model_dump())

    catalog[new_product.id] = new_product

    return new_product


@router.put(
    "/{id}",
    responses={
        200: {"model": Product},
        404: {"model": NotFoundResponse},
    },
)
def update_product(id: UUID, request: ProductCreate):
    """
    Update a product.

    Args:
        product_id (UUID): The ID of the product to update.
        request (ProductCreate): The product to update.

    Returns:
        Product: The updated product, or a 404 if the product with
            the given ID value doesn't exist
    """
    cur_product = catalog.get(id, None)

    if cur_product is None:
        raise HTTPException(status_code=404, detail=f"Product {id} not found")

    kwargs = request.model_dump()
    kwargs["id"] = id
    kwargs["created"] = cur_product.created

    new_product = Product(**kwargs)

    catalog[id] = new_product

    return new_product
