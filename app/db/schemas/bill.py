from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID as py_UUID

from sqlalchemy import UUID, Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .user import UserDb


class BillDb(Base):
    __tablename__ = "bills"

    id: Mapped[py_UUID] = mapped_column(UUID, primary_key=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # optional image url
    paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    modified: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # relationships
    user_id: Mapped[py_UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserDb"] = relationship(back_populates="bills")
