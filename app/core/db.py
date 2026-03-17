# ruff: noqa: E402

from sqlalchemy.orm import declarative_base

Base = declarative_base()

from datetime import datetime
from typing import Any
from uuid import UUID as py_UUID

import orjson
from sqlalchemy import UUID, DateTime, create_engine
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker

from app.config import config

DATABASE_URL = config.DB_URL

if DATABASE_URL is None:
    raise OSError(
        "DATABASE_URL environment variable not set. Failed to determine database url."
    )


def orjson_serializer(obj: Any):
    """
    Note that `orjson.dumps()` return byte array, while sqlalchemy expects string, thus `decode()` call.
    This function helped to solve JSON datetime conversion issue on JSONB column
    """
    return orjson.dumps(
        obj, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NAIVE_UTC
    ).decode()


engine = create_engine(
    DATABASE_URL,
    json_serializer=orjson_serializer,
    json_deserializer=orjson.loads,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Yields a database session.

    The session is automatically rolled back if an exception occurs,
    and automatically closed when the context manager exits.
    """
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()


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
