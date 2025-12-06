from logging import getLogger
from typing import Iterator
from uuid import UUID

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app.db import get_db
from app.exceptions import ConflictError, EntityNotFoundError
from app.models.user import UserCreate, UserPublic, UserUpdate
from app.services.user import UserService

logger = getLogger(__name__)

router = APIRouter(prefix="/v0")


def get_user_service(db: Session = Depends(get_db)) -> Iterator[UserService]:
    """
    Returns a UserService instance using the provided database session.

    The UserService instance is used to encapsulate database operations
    related to users.
    """
    yield UserService(db=db)


@router.get(
    "/users/{id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
        },
    },
    response_model=UserPublic,
    status_code=200,
)
def get_user(
    id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    """
    Returns a single User queried by id

    Args:
        id: the UUID of the User

    Returns:
        a User object if the id matches an existing user in the database

    Raises:
        HttpException with a 404 status if the user cannot be found
    """

    try:
        return service.get_user_by_id(id=id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/users", response_model=list[UserPublic])
def get_all_users(
    service: UserService = Depends(get_user_service),
) -> list[UserPublic]:
    """
    Return a list of all users.

    Returns:
        list[User]: A list of all users.
    """
    return service.get_all_users()


@router.post(
    "/users",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "No users created (empty input list).",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User with the same email already exists.",
        },
    },
    response_model=None,
    status_code=status.HTTP_201_CREATED,
)
def create_users(
    payload: list[UserCreate],
    service: UserService = Depends(get_user_service),
) -> Response | list[UserPublic]:
    """
    Create a list of users from a list of UserCreate objects.

    Args:
        payload (list[UserCreate]): A list of UserCreate objects.

    Returns:
        list[User]: A list of newly created users.

    Raises:
        HTTPException: If a user with the same email already exists.
    """

    try:
        new_users: list[UserPublic] = service.create_users(payload)

        if not new_users:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        return new_users

    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/users/{id}", response_model=UserPublic)
def update_user(
    id: UUID,
    request: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserPublic | None:
    """
    Update an existing user.

    Args:
        id (UUID): The ID of the user to update.
        request (UserCreate): The new user data.

    Returns:
        User: The updated user.

    Raises:
        HTTPException: If the user with the given ID is not found.
    """

    try:
        return service.update_user(id=id, request=request)

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/users/{id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
def delete_user(
    id: UUID,
    service: UserService = Depends(get_user_service),
) -> Response | UserPublic:
    """
    Deletes an existing user.

    Args:
        id (UUID): The ID of the user to delete.

    Returns:
        UserPublic: The deleted user.

    Side-effect:
        The user is removed from the database. If the user
        doesn't exist, this is a no-op, ensuring idempotency.
    """
    try:
        return service.delete_user(id=id)
    except EntityNotFoundError as e:
        return Response(status_code=status.HTTP_200_OK, content=str(e))
