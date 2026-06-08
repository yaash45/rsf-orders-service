from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, exists, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.db import BaseSchema

from ..domain.models import UserCreate, UserPublic
from ..domain.ports import UserPort


class User(BaseSchema):
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


class UserCredentials(BaseSchema):
    """
    Represents authentication-related information for a specific user.
    """

    __tablename__ = "user_credentials"

    # marks if a user's email was verified or not
    # (TODO: remove this later if deciding better auth method)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # references the User that this credential belongs to
    user: Mapped["User"] = mapped_column(
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
    )

    # if this is set to false, a user is not allowed to authenticate
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)



@dataclass
class SqlUserAdapter(UserPort):
    db: Session

    def user_with_email_exists(self, email: str) -> bool:
        return bool(self.db.scalar(select(exists().where(User.email == email))))

    def fetch_all(self) -> Iterable[UserPublic]:
        return self.db.query(User).all()

    def fetch_one(self, user_id: UUID) -> UserPublic | None:
        return self.db.get(User, user_id)

    def find_by_email(self, email: str) -> UserPublic | None:
        return self.db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    def add_user(self, new_user: UserCreate) -> UserPublic:
        user_public = UserPublic(**new_user.model_dump())

        db_user = User(
            id=user_public.id,
            created=user_public.created,
            modified=user_public.modified,
            name=user_public.name,
            email=str(user_public.email),
            kind=user_public.kind.value,
        )

        self.db.add(db_user)
        self.db.commit()

        return user_public
