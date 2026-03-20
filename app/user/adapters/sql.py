from dataclasses import dataclass
from typing import Iterable
from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from ..domain.models import UserCreate, UserPublic
from ..domain.ports import UserPort
from ..schemas import User


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
