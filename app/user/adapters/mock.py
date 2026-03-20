from dataclasses import dataclass, field
from typing import Iterable
from uuid import UUID

from ..domain.models import UserCreate, UserPublic
from ..domain.ports import UserPort


@dataclass
class MockUserAdapter(UserPort):
    _id_map: dict[UUID, UserPublic] = field(default_factory=dict)
    _email_map: dict[str, UserPublic] = field(default_factory=dict)

    def user_with_email_exists(self, email: str) -> bool:
        return email in self._email_map

    def fetch_all(self) -> Iterable[UserPublic]:
        return self._id_map.values()

    def fetch_one(self, user_id: UUID) -> UserPublic | None:
        return self._id_map.get(user_id, None)

    def find_by_email(self, email: str) -> UserPublic | None:
        return self._email_map.get(email, None)

    def add_user(self, new_user: UserCreate) -> UserPublic:
        user = UserPublic(**new_user.model_dump())

        self._id_map[user.id] = user
        self._email_map[str(user.email)] = user

        return user
