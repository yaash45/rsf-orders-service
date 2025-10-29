from uuid import UUID

from fastapi.exceptions import HTTPException
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


@router.post("/", response_model=User, status_code=201)
def create_user(request: UserCreate) -> User:
    """
    Create a new user

    Args:
        request: UserCreate

    Returns:
        User: The newly created user
    """
    new_user = User(**request.model_dump())
    users[new_user.id] = new_user

    return new_user


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
        raise HTTPException(status_code=404, detail=f"Product {id} not found")

    kwargs = request.model_dump()
    kwargs["id"] = user.id
    kwargs["created"] = user.created

    updated_user = User(**kwargs)

    users[user.id] = updated_user

    return updated_user
