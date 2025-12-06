from datetime import datetime, timezone
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field


class Identifiable(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)


class TimeStamped(BaseModel):
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
