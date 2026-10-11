from typing import Any

import orjson
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import config


def orjson_serializer(obj: Any) -> str:
    return orjson.dumps(
        obj, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NAIVE_UTC
    ).decode()


def create_db_engine(database_url: str):
    return create_engine(
        database_url,
        json_serializer=orjson_serializer,
        json_deserializer=orjson.loads,
        connect_args={"check_same_thread": False}
        if database_url.startswith("sqlite")
        else {},
    )


engine = create_db_engine(config.DB_URL) if config.DB_URL is not None else None

SessionLocal = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
    if engine is not None
    else None
)


def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database is not configured.")

    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
