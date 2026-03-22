from datetime import datetime, timezone
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field, field_validator


class Identifiable(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)


class TimeStamped(BaseModel):
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("*", mode="before")
    @classmethod
    def ensure_utc(cls, v):
        # The sqlite database does not store datetimes with the trailing 'Z'.
        #
        # The field validator fixes this by ensuring that any TimeStamped model
        # returned has consistent utc based datetime values.
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v.astimezone(timezone.utc)
        return v
