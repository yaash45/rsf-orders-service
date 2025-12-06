from typing import Self
from uuid import UUID

from pydantic import BaseModel


class NotFoundResponse(BaseModel):
    detail: str


class EntityNotFoundError(Exception):
    @classmethod
    def from_id(cls, entity: str, id: UUID) -> Self:
        return cls(f"'{entity}' with id = '{id}' does not exist.")


class ConflictError(Exception): ...
