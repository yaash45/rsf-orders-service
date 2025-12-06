from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr

from . import Identifiable, TimeStamped


class UserBase(BaseModel):
    name: str
    email: EmailStr
    kind: UserKind


class UserCreate(UserBase, TimeStamped): ...


class UserUpdate(Identifiable):
    name: str | None
    email: str | None
    kind: UserKind | None


class UserPublic(UserBase, Identifiable, TimeStamped):
    model_config = ConfigDict(from_attributes=True)


class UserKind(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"
    TEST = "test"
