from dataclasses import dataclass
from uuid import UUID

from app.core.exceptions import ConflictError, EntityNotFoundError

from .domain.models import UserCreate, UserPublic
from .domain.ports import UserPort


@dataclass(frozen=True)
class UserService:
    """
    Service layer to interact with user-based operations
    """

    port: UserPort

    @classmethod
    def instance(cls, port: UserPort) -> "UserService":
        """
        Construct a new instance of the UserService from
        an object that satisfies the UserPort protocol
        """
        return cls(port)

    def get_all_users(self) -> list[UserPublic]:
        """
        Gets all the users registered in the system
        """
        return list(self.port.fetch_all())

    def get_user(self, user_id: UUID) -> UserPublic:
        """
        Get a user using the user_id
        """

        user = self.port.fetch_one(user_id=user_id)

        if not user:
            raise EntityNotFoundError.from_id("User", user_id)

        return user

    def find_user_by_email(self, email: str) -> UserPublic:
        user = self.port.find_by_email(email)

        if not user:
            raise EntityNotFoundError(f"User with email '{email}' was not found")

        return user

    def setup_new_user(self, new_user: UserCreate) -> UserPublic:
        """
        Sets up a new user in the system
        """

        if self.port.user_with_email_exists(new_user.email):
            raise ConflictError(f"User with email {new_user.email} already exists")

        created_user = self.port.add_user(new_user=new_user)

        return created_user
