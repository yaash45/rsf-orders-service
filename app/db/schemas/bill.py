from datetime import datetime
from uuid import UUID as py_UUID

from sqlalchemy import UUID, Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class BillDb(Base):
    __tablename__ = "Bill"

    id: Mapped[py_UUID] = mapped_column(UUID, primary_key=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # optional image url
    paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    modified: Mapped[datetime] = mapped_column(DateTime, nullable=False)
