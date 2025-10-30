from json import dumps, loads

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

test_app = TestClient(app=app)


def test_create_users_success():
    # one user in request
    payload = [
        {
            "name": "foo",
            "email": "foo@test.com",
            "kind": "admin",
        }
    ]

    result = test_app.post("/users", content=dumps(payload))

    assert result.status_code == status.HTTP_201_CREATED

    created_users = loads(result.content.decode())

    assert isinstance(created_users, list)
    assert len(created_users) == 1
    assert created_users[0].get("name", "") == "foo"
    assert created_users[0].get("email", "") == "foo@test.com"
    assert created_users[0].get("kind", "") == "admin"

    # create multiple users
    payload = [
        {
            "name": "Arnold S.",
            "email": "arnold@test.com",
            "kind": "client",
        },
        {
            "name": "Mark S.",
            "email": "mark.s@lumon.com",
            "kind": "admin",
        },
        {
            "name": "Helly R.",
            "email": "helly.r@lumon.com",
            "kind": "test",
        },
    ]

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


def test_create_user_with_invalid_kind(): ...


def test_create_user_with_duplicate_emails(): ...
