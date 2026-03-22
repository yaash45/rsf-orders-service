from typing import Iterator
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError
from app.db import get_db

from .adapters import SqlUserAdapter
from .domain.models import UserCreate, UserPublic
from .service import UserService

router_v0 = APIRouter(prefix="/v0")


def get_user_service(db: Session = Depends(get_db)) -> Iterator[UserService]:
    """
    Gets an instance of the UserService with the Sql-backed user adapter
    """
    yield UserService.instance(SqlUserAdapter(db=db))


@router_v0.get("/users")
def get_users(
    email: str | None = None,
    service: UserService = Depends(get_user_service),
) -> list[UserPublic]:
    """
    Get all the users registered in the database
    """
    if not email:
        return service.get_all_users()
    else:
        try:
            result = service.find_user_by_email(
                email=email,
            )
        except EntityNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e

        return [result]


@router_v0.get("/users/{user_id}")
def get_user_by_id(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    """
    Gets a user from the database if one exists,
    raises a 404 HTTPException otherwise.
    """
    try:
        result = service.get_user(
            user_id=user_id,
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return result


@router_v0.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
)
def create_new_user(
    request: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    """
    Creates a set of new users in the database
    """
    try:
        result = service.setup_new_user(
            new_user=request,
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return result
