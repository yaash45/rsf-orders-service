from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    kind: UserKind


class User(UserCreate):
    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)


class UserKind(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"
    TEST = "test"
