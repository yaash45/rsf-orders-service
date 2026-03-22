from typing import Iterable, Protocol
from uuid import UUID

from .models import UserCreate, UserPublic


class UserPort(Protocol):
    """
    Port that deals with user registration, access, and credential management
    """

    # User registration and access
    def user_with_email_exists(self, email: str) -> bool:
        """
        Checks if a user with this email address exists in the system
        """
        ...

    def fetch_all(self) -> Iterable[UserPublic]:
        """
        Fetch all the users registered in the system
        """
        ...

    def fetch_one(self, user_id: UUID) -> UserPublic | None:
        """
        Fetches a single user with the provided user ID.

        returns None if user does not exist.
        """
        ...

    def find_by_email(self, email: str) -> UserPublic | None:
        """
        Finds a user by email address
        """

    def add_user(self, new_user: UserCreate) -> UserPublic:
        """
        Creates a new user entry in the system
        """
        ...

    # User credentials related methods
    # TODO: Add methods here
