from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from app.core.service import BaseService
from app.order.domain.models import OrderCreate, OrderPublic, OrderUpdateItems
from app.order.domain.port import OrderPort


@dataclass
class OrderService(BaseService):
    """
    Service for handling orders
    """

    port: OrderPort

    @classmethod
    def instance(cls, port: OrderPort) -> "OrderService":
        return cls(port=port)

    def get_order_by_id(self, order_id: UUID) -> OrderPublic | None:
        """
        Retrieves an order by its ID.

        Args:
            order_id (UUID): The ID of the order to be retrieved.

        Returns:
            OrderPublic | None: The OrderPublic object representing the order, or None if the order does not exist.
        """
        return self.port.get_order_by_id(order_id=order_id)

    def get_orders_by_user_id(self, user_id: UUID) -> Iterable[OrderPublic]:
        """
        Returns an iterator of OrderPublic objects that represent the orders
        made by the user with the given user_id.

        Args:
            user_id (UUID): The ID of the user whose orders are to be retrieved.

        Returns:
            Iterator[OrderPublic]: An iterator of OrderPublic objects.
        """
        return self.port.get_orders_by_user_id(user_id=user_id)

    def create_order(self, request: OrderCreate) -> OrderPublic:
        """
        Creates a new order with the given items.

        Args:
            request (OrderCreate): The request model containing the user ID and items to add to the order.

        Returns:
            OrderPublic: The newly created order with its items.
        """

        return self.port.create_order(request=request)

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
        return self.port.update_order_items(request=request)
