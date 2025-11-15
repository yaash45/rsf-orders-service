from logging import getLogger
from uuid import UUID

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from fastapi.routing import APIRouter
from sqlalchemy import select, update

from ..core.db import SessionLocal
from ..models.user import UserModel
from ..schemas.user import User, UserCreate

logger = getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=list[User])
def get_all_users() -> list[User] | None:
    """
    Return a list of all users.

    Returns:
        list[User]: A list of all users.
    """
    users = []

    with SessionLocal() as db:
        result = db.query(UserModel).all()
        users = [User.model_validate(r, from_attributes=True) for r in result]

    return users


@router.post(
    "/",
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
def create_users(payload: list[UserCreate]) -> Response | list[User]:
    """
    Create a list of users from a list of UserCreate objects.

    Args:
        payload (list[UserCreate]): A list of UserCreate objects.

    Returns:
        list[User]: A list of newly created users.

    Raises:
        HTTPException: If a user with the same email already exists.
    """
    users_to_create = [User(**uc.model_dump()) for uc in payload]

    db_users = []

    for user in users_to_create:
        db_user = UserModel(**user.model_dump())
        db_users.append(db_user)

    with SessionLocal() as db:
        db.add_all(db_users)
        db.commit()

    return users_to_create


@router.put("/{id}", response_model=User)
def update_user(id: UUID, request: UserCreate) -> User | None:
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

    user = None
    updated_user = None

    with SessionLocal() as db:
        user = db.execute(select(UserModel).where(UserModel.id == id)).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with '{id}' not found",
            )

        kwargs = request.model_dump()
        kwargs["id"] = user.id
        kwargs["created"] = user.created

        updated_user = User(**kwargs)
        updated_db_user = UserModel(**updated_user.model_dump())

        db.execute(update(UserModel).where(UserModel.id == id).values(updated_db_user))

    return updated_user
