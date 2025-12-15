from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from app.core.logging import getLogger
from app.db.schemas.user import UserDb
from app.exceptions import ConflictError, EntityNotFoundError
from app.models.user import UserCreate, UserPublic, UserUpdate

from . import BaseService

logger = getLogger(__name__)


class UserService(BaseService):
    def get_user_by_id(self, id: UUID) -> UserPublic:
        """
        Gets a single user from the database by user ID.

        Args:
            id: a UUID representing a user id

        Returns:
            UserPublic model if user id is in the database

        Raises:
            EntityNotFoundError if the user is not found in the database
        """

        db_user: UserDb | None = self.db.execute(
            select(UserDb).where(UserDb.id == id)
        ).scalar_one_or_none()

        if not db_user:
            raise EntityNotFoundError.from_id(entity="User", id=id)

        return UserPublic.model_validate(db_user, from_attributes=True)

    def get_all_users(self) -> list[UserPublic]:
        """
        Gets all the registered users from the database

        Args:
            a list of all the UserPublic models found in the
            database, representing all the registered users and
            their information
        """

        results = self.db.query(UserDb).all()

        return [UserPublic.model_validate(r, from_attributes=True) for r in results]

    def create_users(self, users: list[UserCreate]) -> list[UserPublic]:
        """
        Create a list of users from a list of UserCreate objects.

        Args:
            payload (list[UserCreate]): A list of UserCreate objects.

        Returns:
            list[User]: A list of newly created users.

        Raises:
            ConflictError: If a user with the same email already exists.
        """
        if not users:
            return []

        users_to_create = [UserPublic(**uc.model_dump()) for uc in users]

        db_users: list[UserDb] = []

        for user in users_to_create:
            db_user = UserDb(**user.model_dump())
            db_users.append(db_user)

        try:
            self.db.add_all(db_users)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()

            logger.warning(
                "Bulk user addition failed due to violation of unique email address constraint."
            )
            logger.info("Attempting to add each user one-by-one.")

            errors = []

            for u in db_users:
                try:
                    self.db.add(u)
                    self.db.commit()
                except IntegrityError as e:
                    self.db.rollback()
                    logger.error(f"err = {e}")
                    errors.append(u.email)

            if errors:
                msg = f"Users with emails [{', '.join(errors)}] already exist in system"
                raise ConflictError(msg)

        return users_to_create

    def update_user(self, id: UUID, request: UserUpdate) -> UserPublic:
        """
        Update an existing user.

        Args:
            id (UUID): The ID of the user to update.
            request (UserUpdate): The new user data.

        Returns:
            User: The updated user.

        Raises:
            - EntityNotFoundError: If the user is not found in the database
            - ConflictError: If there is an email conflict with an existing user
        """

        user = None
        updated_user = None

        user = self.db.execute(
            select(UserDb).where(UserDb.id == id)
        ).scalar_one_or_none()

        if user is None:
            raise EntityNotFoundError.from_id(entity="User", id=id)

        kwargs = request.model_dump(exclude_none=True)
        kwargs["id"] = user.id
        kwargs["created"] = user.created
        kwargs["modified"] = datetime.now(tz=timezone.utc)
        updated_user = UserPublic(**kwargs)

        try:
            self.db.execute(update(UserDb).where(UserDb.id == id).values(kwargs))
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            msg = f"User with email '{request.email}' already exists in the system"
            raise ConflictError(msg)

        return updated_user

    def delete_user(self, id: UUID) -> UserPublic:
        """
        Deletes an existing user.

        Args:
            id (UUID): The ID of the user to delete.

        Returns:
            UserPublic: The deleted user.

        Raises:
            - EntityNotFoundError: If the user is not found in the database
        """
        result = self.db.execute(
            delete(UserDb)
            .where(UserDb.id == id)
            .returning(
                UserDb.id,
                UserDb.name,
                UserDb.email,
                UserDb.kind,
                UserDb.created,
                UserDb.modified,
                UserDb.bills,
            )
        ).fetchall()

        if not result:
            msg = f"No-op. User with id '{id}' does not exist"
            logger.warning(msg)
            raise EntityNotFoundError(msg)

        self.db.commit()

        deleted_user = result[0]

        return UserPublic(
            id=deleted_user.id,
            name=deleted_user.name,
            email=deleted_user.email,
            kind=deleted_user.kind,
            created=deleted_user.created,
            modified=deleted_user.modified,
            bills=deleted_user.bills,
        )
