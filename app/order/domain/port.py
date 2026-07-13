from typing import Iterable, Protocol
from uuid import UUID

from app.order.domain.models import OrderCreate, OrderPublic, OrderUpdateItems


class OrderPort(Protocol):
    def get_order_by_id(self, order_id: UUID) -> OrderPublic | None:
        """
        Retrieves an order by its ID.

        Args:
            order_id (UUID): The ID of the order to be retrieved.

        Returns:
            OrderPublic | None: The OrderPublic object representing the order, or None if the order does not exist.
        """
        ...

    def get_orders_by_user_id(self, user_id: UUID) -> Iterable[OrderPublic]:
        """
        Returns an iterator of OrderPublic objects that represent the orders
        made by the user with the given user_id.

        Args:
            user_id (UUID): The ID of the user whose orders are to be retrieved.

        Returns:
            Iterator[OrderPublic]: An iterator of OrderPublic objects.
        """
        ...

    def create_order(self, request: OrderCreate) -> OrderPublic:
        """
        Creates a new order with the given items.

        Args:
            request (OrderCreate): The request model containing the user ID and items to add to the order.

        Returns:
            OrderPublic: The newly created order with its items.
        """
        ...

    def update_order_items(self, request: OrderUpdateItems) -> OrderPublic:
        """
        Updates an existing order with the given items.

        Args:
            request (OrderUpdateItems): The request model containing the order ID and items to update.

        Returns:
            OrderPublic: The updated order with its items.

        Raises:
            EntityNotFoundError: If the order with the given ID does not exist.
        """
        ...
