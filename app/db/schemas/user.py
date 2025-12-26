from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.schemas import BaseSchemaDb

if TYPE_CHECKING:
    from .order import OrderDb


class UserDb(BaseSchemaDb):
    """
    Represents a user in the rsf-orders system
    """

    __tablename__ = "users"

    # basic information
    name: Mapped[str] = mapped_column(
        String, nullable=False
    )  # TODO: consider capping length
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # a label used to specify the type of user (e.g. admin, test, client, etc.)
    kind: Mapped[str] = mapped_column(String(10), nullable=False)

    # all the orders associated with a given user
    orders: Mapped[list["OrderDb"]] = relationship()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, email={self.email}, created={self.created}, kind={self.kind}, id={self.id}>"
