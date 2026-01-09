# ruff: noqa: E402

from sqlalchemy.orm import declarative_base

Base = declarative_base()

from typing import Any

import orjson
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import config
from app.db.schemas import (
    BaseSchemaDb,  # noqa: F401
    BillDb,  # noqa: F401
    OrderDb,  # noqa: F401
    OrderItemDb,  # noqa: F401
    PaymentDb,  # noqa: F401
    ProductDb,  # noqa: F401
    ProductVariantDb,  # noqa: F401
    UserDb,  # noqa: F401
)

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
