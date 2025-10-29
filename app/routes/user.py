from fastapi.routing import APIRouter

from ..models.user import User, UserCreate

router = APIRouter()

users: list[User] = []


@router.get("/", response_model=list[User])
def get_all_users() -> list[User]:
    """
    Return a list of all users.

    Returns:
        list[User]: A list of all users.
    """
    return users


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
    users.append(new_user)

    return new_user
