from typing import Iterator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.order import OrderCreate, OrderPublic, OrderUpdateItems
from app.services.order import OrderService

router = APIRouter(prefix="/v0")


def get_order_service(db: Session = Depends(get_db)) -> Iterator:
    """
    Returns an instance of OrderService that can be used to interact with the database.

    The OrderService instance is used to encapsulate database operations
    related to orders.
    """
    yield OrderService(db=db)


@router.get(
    "/orders/{order_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Order not found",
        },
    },
    response_model=OrderPublic,
    status_code=status.HTTP_200_OK,
)
def get_order_by_id(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> OrderPublic:
    """
    Retrieves an order by its ID.

    Args:
        order_id (UUID): The ID of the order to be retrieved.

    Returns:
        OrderPublic: The OrderPublic object representing the order.
    """
    order = service.get_order_by_id(order_id=order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id: {order_id} does not exist",
        )

    return order


@router.get(
    "/orders/user/{user_id}",
    response_model=list[OrderPublic],
    status_code=status.HTTP_200_OK,
)
def get_order_for_user(
    user_id: UUID,
    service: OrderService = Depends(get_order_service),
):
    return list(service.get_orders_by_user_id(user_id=user_id))


@router.post(
    "/orders",
    response_model=OrderPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    request: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    return service.create_order(request=request)


@router.put(
    "/orders/{id}/items",
    response_model=OrderPublic,
    status_code=status.HTTP_200_OK,
)
def update_order(
    id: UUID,
    request: OrderUpdateItems,
    service: OrderService = Depends(get_order_service),
):
    return service.update_order_items(request=request)
