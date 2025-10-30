from uuid import UUID

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from fastapi.routing import APIRouter

from ..models.user import User, UserCreate

router = APIRouter()

users: dict[UUID, User] = {}


@router.get("/", response_model=list[User])
def get_all_users() -> list[User]:
    """
    Return a list of all users.

    Returns:
        list[User]: A list of all users.
    """
    return list(users.values())


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
    newly_created_users: list[User] = []

    if len(payload) == 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    cur_email_set = {user.email for user in users.values()}

    for item in payload:
        if item.email in cur_email_set:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {item.email} already exists.",
            )

        u = User(**item.model_dump())
        newly_created_users.append(u)
        cur_email_set.add(u.email)

    # once all email uniqueness has been guaranteed, register users
    for user in newly_created_users:
        users[user.id] = user

    return newly_created_users


@router.put("/{id}", response_model=User)
def update_user(id: UUID, request: UserCreate) -> User:
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
    user = users.get(id, None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {id} not found",
        )

    kwargs = request.model_dump()
    kwargs["id"] = user.id
    kwargs["created"] = user.created

    updated_user = User(**kwargs)

    users[user.id] = updated_user

    return updated_user
