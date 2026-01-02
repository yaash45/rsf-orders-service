from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.schemas import BaseSchemaDb


class UserCredentialsDb(BaseSchemaDb):
    """
    Represents authentication-related information for a specific user.
    """

    __tablename__ = "user_credentials"

    # marks if a user's email was verified or not
    # (TODO: remove this later if deciding better auth method)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # references the User that this credential belongs to
    user: Mapped["UserDb"] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        index=True,
        nullable=False,
    )

    # the password hash token stored to validate a user
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    # this credential is valid after this timestamp
    auth_valid_after: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default_factory=lambda: datetime.now(timezone.utc),
    )

    # if this is set to false, a user is not allowed to authenticate
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class UserDb(BaseSchemaDb):
    """
    Represents a user in the rsf-orders system
    """

    __tablename__ = "users"

    # basic information
    name: Mapped[str] = mapped_column(
        String, nullable=False
    )  # TODO: consider capping length
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # a label used to specify the type of user (e.g. admin, test, client, etc.)
    kind: Mapped[str] = mapped_column(String(10), nullable=False)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, email={self.email}, created={self.created}, kind={self.kind}, id={self.id}>"
