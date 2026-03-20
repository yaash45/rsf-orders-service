from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.models import Identifiable, TimeStamped


class UserKind(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"
    TEST = "test"


class UserBase(BaseModel):
    name: str
    email: EmailStr
    kind: UserKind


class UserCreate(UserBase, TimeStamped): ...


class UserPublic(UserBase, Identifiable, TimeStamped):
    model_config = ConfigDict(from_attributes=True)
