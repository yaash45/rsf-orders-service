from json import dumps, loads

from fastapi import status
from fastapi.testclient import TestClient
from pytest import fixture

from app.main import app

test_app = TestClient(app=app)


@fixture(autouse=True)
def clear_users():
    """
    Clears the users on the server after each test.
    """
    from app.routes.user import users

    users.clear()


def _build_create_users_payload(
    data: list[tuple[str, str, str]],
) -> list[dict[str, str]]:
    """
    Builds a http request payload for the POST request
    to the /users endpoint. The format of the payload looks like this:

    [
        {"name": "item1", "email": "item1@test.com", "kind": "admin"},
        {"name": "item2", "email": "item2@test.com", "kind": "admin"},
        ...
    ]
    """
    return [{"name": item[0], "email": item[1], "kind": item[2]} for item in data]


def test_create_users_success():
    # one user in request
    payload = _build_create_users_payload(
        [
            ("foo", "foo@test.com", "admin"),
        ],
    )

    result = test_app.post("/users", content=dumps(payload))

    assert result.status_code == status.HTTP_201_CREATED

    created_users = loads(result.content.decode())

    assert isinstance(created_users, list)
    assert len(created_users) == 1
    assert created_users[0].get("name", "") == "foo"
    assert created_users[0].get("email", "") == "foo@test.com"
    assert created_users[0].get("kind", "") == "admin"

    # create multiple users
    payload = _build_create_users_payload(
        [
            ("Arnold S.", "arnold@test.com", "client"),
            ("Mark S.", "mark.s@lumon.com", "admin"),
            ("Helly R.", "helly.r@lumon.com", "test"),
        ],
    )

    result = test_app.post("/users", content=dumps(payload))

    assert result.status_code == status.HTTP_201_CREATED

    created_users = loads(result.content.decode())

    assert isinstance(created_users, list)
    assert len(created_users) == 3

    created_user_names = sorted([u.get("name", "") for u in created_users])
    assert created_user_names == [
        "Arnold S.",
        "Helly R.",
        "Mark S.",
    ]

    created_user_emails = sorted([u.get("email", "") for u in created_users])
    assert created_user_emails == [
        "arnold@test.com",
        "helly.r@lumon.com",
        "mark.s@lumon.com",
    ]

    # empty payload
    payload = []

    result = test_app.post("/users", content=dumps(payload))

    assert result.status_code == status.HTTP_204_NO_CONTENT

    # try get request
    result = test_app.get("/users")

    assert result.status_code == status.HTTP_200_OK

    all_users = loads(result.content)

    assert isinstance(all_users, list)
    assert len(all_users) == 4

    all_user_names = sorted([u.get("name", "") for u in all_users])
    assert all_user_names == [
        "Arnold S.",
        "Helly R.",
        "Mark S.",
        "foo",
    ]


def test_create_user_with_invalid_kind():
    """
    The user's in the system will have a kind value,
    that falls in a finite set of strings.

    This test verifies if the server handles
    invalid kind values appropriately
    """
    # valid request
    payload = _build_create_users_payload(
        [
            ("foo", "foo@test.com", "admin"),
        ]
    )

    result = test_app.post("/users", content=dumps(payload))

    assert result.status_code == status.HTTP_201_CREATED

    # invalid request
    payload = _build_create_users_payload(
        [
            ("test", "foo@test.com", "user"),  # invalid kind value
        ]
    )

    result = test_app.post("/users", content=dumps(payload))

    assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_user_with_duplicate_emails():
    """
    Tests that the server ensures that all email addresses
    entered into the system are unique
    """

    # ensure uniqueness within same request
    payload = _build_create_users_payload(
        [
            ("test", "test@gmail.com", "admin"),
            ("other_test", "test@gmail.com", "client"),
        ]
    )

    result = test_app.post("/users", content=dumps(payload))

    assert result.status_code == status.HTTP_400_BAD_REQUEST

    # ensure uniqueness across two different requests
    result = test_app.post(
        "/users",
        content=dumps(
            _build_create_users_payload(
                [("Arnold S", "arnold@terminator.com", "client")]
            )
        ),
    )

    assert result.status_code == status.HTTP_201_CREATED

    result = test_app.post(
        "/users",
        content=dumps(
            _build_create_users_payload(
                [
                    ("Some Other Arnold S", "arnold@terminator.com", "client"),
                    ("James C", "james@pandora.com", "test"),
                ]
            )
        ),
    )

    assert result.status_code == status.HTTP_400_BAD_REQUEST


def test_update_user():
    # add one user
    response = test_app.post(
        "/users",
        content=dumps(
            _build_create_users_payload(
                [
                    ("test", "test@foo.com", "test"),
                ],
            ),
        ),
    )

    new_user = loads(response.content)[0]

    # modify user
    response = test_app.put(
        f"/users/{new_user.get('id', '')}",
        content=dumps(
            _build_create_users_payload(
                [
                    ("test", "test_new@foo.com", "admin"),
                ]
            ).pop(),  # popping because payload is returned as a list
        ),
    )

    assert response.status_code == status.HTTP_200_OK

    # get the user
    response = test_app.get("/users")
    modified_user = loads(response.content)[0]
    assert modified_user.get("email", "") == "test_new@foo.com"

    # even a PUT request should ensure email uniqueness
    response = test_app.post(
        "/users",
        content=dumps(
            _build_create_users_payload(
                [
                    ("arnold", "arnold@foo.com", "test"),
                ],
            )
        ),
    )

    new_user = loads(response.content)[0]

    response = test_app.put(
        f"/users/{new_user.get('id', '')}",
        content=dumps(
            _build_create_users_payload(
                [
                    ("arnold", "test_new@foo.com", "test"),
                ],
            ).pop(),
        ),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
