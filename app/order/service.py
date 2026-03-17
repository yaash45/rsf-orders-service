from datetime import datetime, timezone
from typing import Iterable
from uuid import UUID

from pydantic import ValidationError

from app.core.service import BaseService
from app.exceptions import EntityNotFoundError
from app.order.models import OrderCreate, OrderPublic, OrderStatus, OrderUpdateItems
from app.order.schemas import OrderDb, OrderItemDb
from app.product.schemas import ProductVariantDb


class OrderService(BaseService):
    """
    Service for handling orders
    """

    def get_order_by_id(self, order_id: UUID) -> OrderPublic | None:
        """
        Retrieves an order by its ID.

        Args:
            order_id (UUID): The ID of the order to be retrieved.

        Returns:
            OrderPublic | None: The OrderPublic object representing the order, or None if the order does not exist.
        """
        return self.db.get(OrderDb, order_id)

    def get_orders_by_user_id(self, user_id: UUID) -> Iterable[OrderPublic]:
        """
        Returns an iterator of OrderPublic objects that represent the orders
        made by the user with the given user_id.

        Args:
            user_id (UUID): The ID of the user whose orders are to be retrieved.

        Returns:
            Iterator[OrderPublic]: An iterator of OrderPublic objects.
        """
        return self.db.query(OrderDb).filter(OrderDb.user_id == user_id).all()

    def _extract_validated_items(
        self, variant_map: dict[UUID, int]
    ) -> list[OrderItemDb]:
        """
        Validates and extracts OrderItemDb objects from a given variant map.

        Args:
            variant_map (dict[UUID, int]): A dictionary mapping product variant IDs to their quantities.

        Returns:
            list[OrderItemDb]: A list of OrderItemDb objects representing the validated items.

        Raises:
            ValidationError: If any of the quantities are invalid (i.e. <= 0).
            EntityNotFoundError: If any of the product variants do not exist.
        """
        result: list[OrderItemDb] = []

        for variant_id, quantity in variant_map.items():
            if quantity <= 0:
                raise ValidationError(
                    f"Invalid quantity '{quantity}'. Must be a non-zero positive integer."
                )

            if not self.db.get(ProductVariantDb, variant_id):
                raise EntityNotFoundError("Product variant", variant_id)

            result.append(
                OrderItemDb(
                    product_variant_id=variant_id,
                    quantity=quantity,
                )
            )

        return result

    def create_order(self, request: OrderCreate) -> OrderPublic:
        """
        Creates a new order with the given items.

        Args:
            request (OrderCreate): The request model containing the user ID and items to add to the order.

        Returns:
            OrderPublic: The newly created order with its items.
        """

        with self.db.begin():
            db_order = OrderDb(
                status=OrderStatus.PENDING,
                status_timestamp=datetime.now(tz=timezone.utc),
                user_id=request.user_id,
            )

            self.db.add(db_order)
            # flush here to generate UUID which can be used in public model
            self.db.flush()

            validated_db_items: list[OrderItemDb] = self._extract_validated_items(
                request.items
            )

            db_order.items.extend(validated_db_items)

        new_order = OrderPublic.model_validate(db_order)

        return new_order

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
        with self.db.begin():
            db_order: OrderDb | None = self.db.get(OrderDb, request.id)

            if not db_order:
                raise EntityNotFoundError.from_id("Order", request.id)

            db_order.items = self._extract_validated_items(request.items)

        return OrderPublic.model_validate(db_order)
