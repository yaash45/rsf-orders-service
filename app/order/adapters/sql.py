from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Iterable
from uuid import UUID as py_UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.exceptions import EntityNotFoundError
from app.db import Base, BaseSchema
from app.order.domain.models import (
    OrderCreate,
    OrderItemPublic,
    OrderPublic,
    OrderStatus,
    OrderUpdateItems,
)
from app.order.domain.port import OrderPort
from app.product.adapters.sql import ProductVariant

if TYPE_CHECKING:
    from app.bill.adapters.sql import Bill


class OrderItem(Base):
    """
    Represents an item that is part of an order, specifying the product,
    its variant, and quantity
    """

    __tablename__ = "order_items"

    # the order that this item is associated with
    order_id: Mapped[py_UUID] = mapped_column(
        ForeignKey("orders.id"),
        primary_key=True,
    )

    # the product and its variant that is being ordered
    product_variant_id: Mapped[py_UUID] = mapped_column(
        ForeignKey("product_variants.id"),
        primary_key=True,
    )

    # quantity of the product ordered
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)


class Order(BaseSchema):
    """
    Represents the orders made by various users
    """

    __tablename__ = "orders"

    # order status related fields
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, values_callable=lambda enum: [e.value for e in enum]),
        nullable=False,
    )
    status_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # refer to the user that placed the order
    user_id: Mapped[py_UUID] = mapped_column(ForeignKey("users.id"))

    # tracks which products were ordered, and how many
    items: Mapped[list["OrderItem"]] = relationship()

    # bill associated with the order
    bill: Mapped["Bill | None"] = relationship(
        "Bill",
        uselist=False,
        back_populates="order",
    )


@dataclass
class SqlOrderAdapter(OrderPort):
    db: Session

    def get_order_by_id(self, order_id: py_UUID) -> OrderPublic | None:
        """
        Retrieves an order by its ID.

        Args:
            order_id (UUID): The ID of the order to be retrieved.

        Returns:
            OrderPublic | None: The OrderPublic object representing the order, or None if the order does not exist.
        """
        return self.db.get(Order, order_id)

    def get_orders_by_user_id(self, user_id: py_UUID) -> Iterable[OrderPublic]:
        """
        Returns an iterator of OrderPublic objects that represent the orders
        made by the user with the given user_id.

        Args:
            user_id (UUID): The ID of the user whose orders are to be retrieved.

        Returns:
            Iterator[OrderPublic]: An iterator of OrderPublic objects.
        """
        return self.db.query(Order).filter(Order.user_id == user_id).all()

    def _extract_validated_items(
        self, variants: list[OrderItemPublic]
    ) -> list[OrderItem]:
        """
        Validates and extracts OrderItem objects from a given variant map.

        Args:
            variant_map (dict[UUID, int]): A dictionary mapping product variant IDs to their quantities.

        Returns:
            list[OrderItem]: A list of OrderItem objects representing the validated items.

        Raises:
            ValueError: If any of the quantities are invalid (i.e. <= 0).
            EntityNotFoundError: If any of the product variants do not exist.
        """
        result: list[OrderItem] = []

        for item in variants:
            if not self.db.get(ProductVariant, item.product_variant_id):
                raise EntityNotFoundError("Product variant", item.product_variant_id)

            result.append(
                OrderItem(
                    product_variant_id=item.product_variant_id,
                    quantity=item.quantity,
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

        new_order = OrderPublic(**request.model_dump())

        with self.db.begin():
            db_order = Order(
                id=new_order.id,
                created=new_order.created,
                modified=new_order.modified,
                status=new_order.status,
                status_timestamp=new_order.status_timestamp,
                user_id=new_order.user_id,
            )

            self.db.add(db_order)
            # flush here to generate UUID which can be used in public model
            self.db.flush()

            validated_db_items: list[OrderItem] = self._extract_validated_items(
                request.items
            )

            db_order.items.extend(validated_db_items)

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
            db_order: Order | None = self.db.get(Order, request.id)

            if not db_order:
                raise EntityNotFoundError.from_id("Order", request.id)

            db_order.items = self._extract_validated_items(request.items)

        return OrderPublic.model_validate(db_order)
