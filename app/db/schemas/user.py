from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID as py_UUID

from sqlalchemy import UUID, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .bill import BillDb


class UserDb(Base):
    __tablename__ = "users"

    id: Mapped[py_UUID] = mapped_column(UUID, primary_key=True)
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    modified: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    name: Mapped[str] = mapped_column(
        String, nullable=False
    )  # TODO: consider capping length
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(10), nullable=False)

    # relationships
    bills: Mapped[list["BillDb"]] = relationship()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, email={self.email}, created={self.created}, kind={self.kind}, id={self.id}>"
