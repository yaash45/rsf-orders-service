from datetime import datetime
from uuid import UUID as py_UUID

from sqlalchemy import UUID, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class BaseSchemaDb(Base):
    """
    Base class for all database schemas. This schema represents an
    abstract table which is:

        1) Identifiable: the primary key is a UUID
        2) Timestamped: tracks creation and modification timestamps
    """

    __abstract__ = True

    # make the primary key a UUID
    id: Mapped[py_UUID] = mapped_column(
        UUID,
        primary_key=True,
    )

    # track timestamps of creation and modification
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
