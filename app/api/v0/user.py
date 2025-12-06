from datetime import datetime, timezone
from logging import getLogger
from uuid import UUID

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from fastapi.routing import APIRouter
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.db.schemas.user import User as UserModel
from app.models.user import UserCreate, UserPublic, UserUpdate

logger = getLogger(__name__)

router = APIRouter(prefix="/v0")


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
def get_user_by_id(id: UUID, db: Session = Depends(get_db)) -> UserPublic:
    """
    Returns a single User queried by id

    Args:
        id: the UUID of the User

    Returns:
        a User object if the id matches an existing user in the database

    Raises:
        HttpException with a 404 status if the user cannot be found
    """

    db_user = db.execute(
        select(UserModel).where(UserModel.id == id)
    ).scalar_one_or_none()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id = {id} not found.",
        )

    return UserPublic.model_validate(db_user, from_attributes=True)


@router.get("/users", response_model=list[UserPublic])
def get_all_users(db: Session = Depends(get_db)) -> list[UserPublic]:
    """
    Return a list of all users.

    Returns:
        list[User]: A list of all users.
    """
    users = []
    result = db.query(UserModel).all()
    users = [UserPublic.model_validate(r, from_attributes=True) for r in result]

    return users


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
    payload: list[UserCreate], db: Session = Depends(get_db)
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
    if not payload:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    users_to_create = [UserPublic(**uc.model_dump()) for uc in payload]

    db_users: list[UserModel] = []

    for user in users_to_create:
        db_user = UserModel(**user.model_dump())
        db_users.append(db_user)

    try:
        db.add_all(db_users)
        db.commit()
    except IntegrityError:
        db.rollback()

        logger.warning(
            "Bulk user addition failed due to violation of unique email address constraint."
        )
        logger.info("Attempting to add each user one-by-one.")

        errors = []

        for u in db_users:
            try:
                db.add(u)
                db.commit()
            except IntegrityError as e:
                db.rollback()
                logger.error(f"err = {e}")
                errors.append(u.email)

        if errors:
            msg = f"Users with emails [{', '.join(errors)}] already exist in system"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg,
            )

    return users_to_create


@router.put("/users/{id}", response_model=UserPublic)
def update_user(
    id: UUID, request: UserUpdate, db: Session = Depends(get_db)
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

    user = None
    updated_user = None

    user = db.execute(select(UserModel).where(UserModel.id == id)).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with '{id}' not found",
        )

    kwargs = request.model_dump(exclude_none=True)
    kwargs["id"] = user.id
    kwargs["created"] = user.created
    kwargs["modified"] = datetime.now(tz=timezone.utc)
    updated_user = UserPublic(**kwargs)

    try:
        db.execute(update(UserModel).where(UserModel.id == id).values(kwargs))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{request.email}' already exists in the system",
        )

    return updated_user


@router.delete("/users/{id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
def delete_user(id: UUID, db: Session = Depends(get_db)) -> Response | UserPublic:
    result = db.execute(
        delete(UserModel)
        .where(UserModel.id == id)
        .returning(
            UserModel.id,
            UserModel.name,
            UserModel.email,
            UserModel.kind,
            UserModel.created,
        )
    ).fetchall()

    if not result:
        msg = f"No-op. User with id '{id}' does not exist"
        logger.info(msg)
        return Response(status_code=status.HTTP_200_OK, content=msg)

    db.commit()

    deleted_user = result[0]

    return UserPublic(
        id=deleted_user.id,
        name=deleted_user.name,
        email=deleted_user.email,
        kind=deleted_user.kind,
        created=deleted_user.created,
    )
