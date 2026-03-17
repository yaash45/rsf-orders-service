from typing import Self
from uuid import UUID


class EntityNotFoundError(Exception):
    """
    Raised when an entity is not found in the database.

    This exception is raised when an API endpoint is called with a valid
    UUID, but the corresponding entity is not found in the database.
    """

    @classmethod
    def from_id(cls, entity: str, id: UUID) -> Self:
        """
        Creates an EntityNotFoundError with a message describing a non-existent
        entity with a given id.

        Args:
            entity (str): The name of the entity.
            id (UUID): The id of the entity.

        Returns:
            EntityNotFoundError: An instance of EntityNotFoundError with a message
            describing the non-existent entity with the given id.
        """
        return cls(f"'{entity}' with id = '{id}' does not exist.")


class ConflictError(Exception):
    """
    Raised when a request conflicts with the current state of the resource.

    For example, if a user attempts to create a resource with an email that
    already exists, a ConflictError will be raised.
    """
